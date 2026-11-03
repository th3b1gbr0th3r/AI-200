# =============================================================================
# Fill in the four values below with what you collected in the lab, then save.
# =============================================================================

rg                    = "ResourceMoverRG-eastus-southeastasia-sea"    # Existing resource group name (Task 3)
location              = "southeastasia"            # Azure region in CLI format, e.g. eastus, eastus2 (Task 3)
foundryEndpoint       = "https://<recurso>.openai.azure.com/"  # OpenAI endpoint URL (Task 3), e.g. https://<your-resource-name>.openai.azure.com/
foundryDeploymentName = "gpt-5.1"   # Model deployment name (Task 2), e.g. gpt-5.1

# If the Standard_D2s_v3 SKU is not available in your region, try using
# Standard_D2s_v4, or Standard_D2s_v5 instead.
AKS_VM_SIZE = "Standard_D2s_v3"

# =============================================================================
# DON'T CHANGE ANYTHING BELOW THIS LINE.
# =============================================================================

import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

API_IMAGE_NAME = "aks-api"

# Suppress Azure CLI preview / deprecation WARNINGs from every subprocess call.
os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")

_EXE_CACHE: dict[str, str] = {}


def _resolve_exe(name: str) -> str:
    """Locate an executable on PATH (handles az.cmd / kubectl.exe on Windows)."""
    cached = _EXE_CACHE.get(name)
    if cached:
        return cached
    resolved = shutil.which(name)
    if not resolved:
        print(f"Error: '{name}' not found on PATH. Install it and retry.")
        sys.exit(1)
    _EXE_CACHE[name] = resolved
    return resolved


def run_quiet(description: str, argv: list[str]) -> bool:
    """Run a command, print an error on failure, return success as bool."""
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        combined = (result.stdout or "") + (result.stderr or "")
        if combined.strip():
            print(combined.rstrip())
        return False
    return True


def az_query(argv: list[str]) -> str:
    """Run an `az ... -o tsv` probe and return stripped stdout (or empty)."""
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def clear_screen() -> None:
    """Clear the terminal across bash, zsh, PowerShell, cmd, and Git Bash."""
    cmd = "cls" if os.name == "nt" else "clear"
    if os.system(cmd) != 0:
        sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
        sys.stdout.flush()


def pause(prompt: str = "Press Enter to continue...") -> None:
    try:
        input(prompt)
    except EOFError:
        print()


def require_az_login() -> str:
    """Return the signed-in user's object id, or exit if not logged in."""
    user_object_id = az_query(
        ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"]
    )
    if not user_object_id:
        print("Error: Not authenticated with Azure. Please run: az login")
        sys.exit(1)
    return user_object_id


def write_env_files(env_vars: dict[str, str], directory: str = ".") -> None:
    """Write .env (bash) and .env.ps1 (PowerShell) side by side.

    Writes UTF-8 without BOM and LF line endings so both bash `source` and
    PowerShell dot-source read them correctly on every supported shell.
    """
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    def bash_escape(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("$", "\\$")
            .replace("`", "\\`")
        )

    def ps_escape(value: str) -> str:
        return (
            value.replace("`", "``")
            .replace('"', '`"')
            .replace("$", "`$")
        )

    bash_lines = [f'export {k}="{bash_escape(v)}"\n' for k, v in env_vars.items()]
    ps_lines = [f'$env:{k} = "{ps_escape(v)}"\n' for k, v in env_vars.items()]

    with open(target_dir / ".env", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(bash_lines)
    with open(target_dir / ".env.ps1", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(ps_lines)


def _foundry_resource_name(endpoint: str) -> str:
    """Parse the Foundry/OpenAI resource name from its endpoint URL.

    "https://my-resource.openai.azure.com/" -> "my-resource"
    Returns an empty string when the endpoint is blank or unparseable.
    """
    if not endpoint:
        return ""
    host = endpoint.split("://", 1)[-1].split("/", 1)[0]
    return host.split(".", 1)[0] if host else ""


def _derived_names(user_object_id: str) -> tuple[str, str]:
    user_hash = hashlib.sha1(user_object_id.encode("utf-8")).hexdigest()[:8]
    return (
        f"acr{user_hash}",
        f"aks-{user_hash}",
    )


def show_menu(acr_name: str, aks_cluster: str) -> None:
    clear_screen()
    print("=====================================================================")
    print("    AKS Deployment with Foundry Model Integration")
    print("=====================================================================")
    print(f"Resource Group: {rg}")
    print(f"Location: {location}")
    print(f"Foundry Endpoint: {foundryEndpoint}")
    print(f"Model Deployment: {foundryDeploymentName}")
    print(f"ACR Name: {acr_name}")
    print(f"AKS Cluster: {aks_cluster}")
    print("=====================================================================")
    print("1. Create Azure Container Registry (ACR)")
    print("2. Build and push API image to ACR")
    print("3. Create AKS cluster")
    print("4. Check deployment status")
    print("5. Deploy to AKS")
    print("6. Delete failed AKS deployment")
    print("7. Exit")
    print("=====================================================================")


def create_resource_group() -> bool:
    print(f"Checking/creating resource group '{rg}'...")
    exists = az_query(["az", "group", "exists", "--name", rg])
    if exists == "false":
        if not run_quiet(
            "Create resource group",
            [
                "az", "group", "create",
                "--name", rg,
                "--location", location,
            ],
        ):
            return False
        print(f"Resource group created: {rg}")
    else:
        print(f"Resource group already exists: {rg}")
    return True


def create_acr(acr_name: str) -> bool:
    print(f"Creating Azure Container Registry '{acr_name}'...")
    existing = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "name", "-o", "tsv"]
    )
    if not existing:
        if not run_quiet(
            "Create Azure Container Registry",
            [
                "az", "acr", "create",
                "--resource-group", rg,
                "--name", acr_name,
                "--sku", "Basic",
                "--admin-enabled", "true",
            ],
        ):
            return False
        print(f"ACR created: {acr_name}")
    else:
        print(f"ACR already exists: {acr_name}")
    return True


def build_and_push_image(acr_name: str) -> bool:
    print("Building and pushing API image to ACR...")
    acr_server = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "loginServer", "-o", "tsv"]
    )
    if not acr_server:
        print("Error: Could not retrieve ACR login server.")
        return False

    if not run_quiet(
        "Build and push API image",
        [
            "az", "acr", "build",
            "--resource-group", rg,
            "--registry", acr_name,
            "--image", f"{API_IMAGE_NAME}:latest",
            "--file", "api/Dockerfile",
            "--no-logs",
            "api/",
        ],
    ):
        return False

    print(f"Image built and pushed: {acr_server}/{API_IMAGE_NAME}:latest")
    return True


def _print_aks_failure_hint() -> None:
    print()
    print("The AKS deployment failed. Review the Azure error details above.")
    print("Quota checks can fail before a cluster is created, while later failures")
    print("can leave a cluster in a Failed state. Use option 4 to check the status.")
    print("For regional capacity or SKU availability errors, change the 'location'")
    print("variable near the top of this script. For quota errors, use a region with")
    print("available quota or request a quota increase.")
    print("Correct the reported issue, then use option 6 to delete any failed deployment.")


def create_aks_cluster(acr_name: str, aks_cluster: str) -> bool:
    aks_state = az_query(
        ["az", "aks", "show", "--resource-group", rg, "--name", aks_cluster,
         "--query", "provisioningState", "-o", "tsv"]
    )
    if aks_state == "Succeeded":
        print(f"AKS cluster already exists: {aks_cluster} (State: {aks_state})")
        return True
    if aks_state in ("Failed", "Canceled"):
        print(f"Error: AKS cluster '{aks_cluster}' is in a {aks_state} state.")
        print("Review the Azure error, correct the underlying issue, then use option 6")
        print("to delete the failed deployment before running option 3 again.")
        return False
    if aks_state:
        print(f"AKS cluster '{aks_cluster}' is still provisioning (State: {aks_state}).")
        print("Please wait for it to finish, then check the deployment status from the menu.")
        return True

    print(f"Creating AKS cluster '{aks_cluster}' with one {AKS_VM_SIZE} node...")
    print("This may take 5-10 minutes to complete. Please wait...")
    print()
    start = time.monotonic()

    if not run_quiet(
        "Create AKS cluster",
        [
            "az", "aks", "create",
            "--resource-group", rg,
            "--location", location,
            "--name", aks_cluster,
            "--node-count", "1",
            "--node-vm-size", AKS_VM_SIZE,
            "--tier", "free",
            "--vm-set-type", "VirtualMachineScaleSets",
            "--load-balancer-sku", "standard",
            "--enable-managed-identity",
            "--network-plugin", "azure",
            "--no-ssh-key",
            "--attach-acr", acr_name,
        ],
    ):
        _print_aks_failure_hint()
        return False

    elapsed = int(time.monotonic() - start)
    minutes, seconds = divmod(elapsed, 60)
    print(f"AKS cluster creation completed: {aks_cluster}")
    print(f"  Deployment time: {minutes}m {seconds}s")
    return True


def delete_failed_aks_deployment(aks_cluster: str) -> bool:
    aks_state = az_query(
        ["az", "aks", "show", "--resource-group", rg, "--name", aks_cluster,
         "--query", "provisioningState", "-o", "tsv"]
    )

    if not aks_state:
        print(f"No AKS deployment was found: {aks_cluster}")
        return True

    if aks_state not in ("Failed", "Canceled"):
        print(f"Error: Refusing to delete AKS cluster '{aks_cluster}' (State: {aks_state}).")
        print("This option only deletes deployments in a Failed or Canceled state.")
        return False

    print(f"WARNING: This permanently deletes AKS cluster '{aks_cluster}' and its")
    print("AKS-managed resources. This action cannot be undone.")
    confirm = input("Are you sure you want to delete the failed deployment? (yes/no): ")

    if confirm != "yes":
        print("Deletion canceled.")
        return True

    if not run_quiet(
        "Delete failed AKS deployment",
        [
            "az", "aks", "delete",
            "--resource-group", rg,
            "--name", aks_cluster,
            "--yes",
        ],
    ):
        return False

    print(f"Failed AKS deployment deleted: {aks_cluster}")
    return True


def _kubectl_apply_from_stdin(description: str, yaml_text: str, namespace: str = "default") -> bool:
    """Pipe YAML text to `kubectl apply -f -` in the given namespace."""
    kubectl = _resolve_exe("kubectl")
    result = subprocess.run(
        [kubectl, "apply", "-f", "-", "-n", namespace],
        input=yaml_text, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        combined = (result.stdout or "") + (result.stderr or "")
        if combined.strip():
            print(combined.rstrip())
        return False
    return True


def deploy_to_aks(acr_name: str, aks_cluster: str) -> bool:
    print("Deploying application to AKS...")
    print()

    print("Getting AKS credentials...")
    if not run_quiet(
        "Get AKS credentials",
        [
            "az", "aks", "get-credentials",
            "--resource-group", rg,
            "--name", aks_cluster,
            "--overwrite-existing",
        ],
    ):
        return False
    print("AKS credentials configured")
    print()

    foundry_resource = _foundry_resource_name(foundryEndpoint)
    if not foundry_resource:
        print("Error: Could not parse the Foundry resource name from foundryEndpoint.")
        print("Check that foundryEndpoint looks like https://<your-resource-name>.openai.azure.com/")
        return False

    print("Assigning Cognitive Services OpenAI User role to AKS identity...")
    kubelet_identity = az_query(
        ["az", "aks", "show", "--name", aks_cluster, "--resource-group", rg,
         "--query", "identityProfile.kubeletidentity.objectId", "-o", "tsv"]
    )
    foundry_resource_id = az_query(
        ["az", "cognitiveservices", "account", "show",
         "--name", foundry_resource, "--resource-group", rg,
         "--query", "id", "-o", "tsv"]
    )
    if not kubelet_identity or not foundry_resource_id:
        print("Error: Could not retrieve AKS identity or Foundry resource ID.")
        print("Check that the resource group and foundryEndpoint values are correct.")
        return False

    if not run_quiet(
        "Assign Cognitive Services OpenAI User role",
        [
            "az", "role", "assignment", "create",
            "--assignee-object-id", kubelet_identity,
            "--assignee-principal-type", "ServicePrincipal",
            "--role", "Cognitive Services OpenAI User",
            "--scope", foundry_resource_id,
        ],
    ):
        return False
    print("Role assigned to AKS kubelet identity (may take 1-2 minutes to propagate)")
    print()

    print("Deploying Kubernetes manifests...")
    deployment_yaml = Path("k8s/deployment.yaml").read_text(encoding="utf-8")
    deployment_yaml = deployment_yaml.replace("ACR_ENDPOINT", f"{acr_name}.azurecr.io")
    deployment_yaml = deployment_yaml.replace("FOUNDRY_ENDPOINT", foundryEndpoint)
    # The model deployment is now created by hand in the portal, so its name comes
    # from foundryDeploymentName. Substitute both the manifest placeholder and the
    # previous fixed name so the API pod targets the correct model deployment.
    deployment_yaml = deployment_yaml.replace("FOUNDRY_DEPLOYMENT_NAME", foundryDeploymentName)
    deployment_yaml = deployment_yaml.replace("gpt-5-mini", foundryDeploymentName)
    if not _kubectl_apply_from_stdin("Apply deployment manifest", deployment_yaml):
        return False
    print(f"Deployment manifest updated with ACR endpoint: {acr_name}.azurecr.io and Foundry endpoint")

    service_yaml = Path("k8s/service.yaml").read_text(encoding="utf-8")
    if not _kubectl_apply_from_stdin("Apply service manifest", service_yaml):
        return False
    print("Service manifest applied")
    print()

    print("Waiting for LoadBalancer external IP (this may take a few minutes)...")
    kubectl = _resolve_exe("kubectl")
    external_ip = ""
    for _ in range(60):
        result = subprocess.run(
            [kubectl, "get", "svc", "aks-api-service",
             "-o", "jsonpath={.status.loadBalancer.ingress[0].ip}",
             "-n", "default"],
            capture_output=True, text=True, check=False,
        )
        candidate = (result.stdout or "").strip()
        if candidate and not candidate.startswith("10."):
            external_ip = candidate
            break
        time.sleep(2)

    if not external_ip:
        print("Error: Could not obtain external IP for the service.")
        print("You can check the service status manually with: kubectl get svc aks-api-service")
        return False
    print(f"External IP obtained: {external_ip}")
    print()

    print("Updating client/.env and client/.env.ps1 with API endpoint...")
    write_env_files({"API_ENDPOINT": f"http://{external_ip}"}, directory="client")
    print("client/.env and client/.env.ps1 updated")
    print()
    print("==========================================")
    print("Deployment completed successfully!")
    print("==========================================")
    print(f"API Endpoint: http://{external_ip}")
    print()
    print("Next steps:")
    print("1. Run the client to test the API:")
    print("   python client/main.py")
    print("==========================================")
    return True


def check_deployment_status(acr_name: str, aks_cluster: str) -> bool:
    print("Checking deployment status...")
    print()

    foundry_resource = _foundry_resource_name(foundryEndpoint)
    print(f"Foundry Model Deployment ({foundryDeploymentName}):")
    if foundry_resource:
        foundry_status = az_query(
            ["az", "cognitiveservices", "account", "deployment", "show",
             "--name", foundry_resource, "--resource-group", rg,
             "--deployment-name", foundryDeploymentName,
             "--query", "properties.provisioningState", "-o", "tsv"]
        )
        if foundry_status:
            print(f"  Status: {foundry_status}")
            if foundry_status == "Succeeded":
                print("  Model deployed and ready")
        else:
            print("  Status: Not found (verify foundryEndpoint and foundryDeploymentName)")
    else:
        print("  Status: Could not parse resource name from foundryEndpoint")

    print()
    print(f"Azure Container Registry ({acr_name}):")
    acr_status = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "provisioningState", "-o", "tsv"]
    )
    if acr_status:
        print(f"  Status: {acr_status}")
    else:
        print("  Status: Not found or not ready")

    print()
    print(f"AKS Cluster ({aks_cluster}):")
    aks_status = az_query(
        ["az", "aks", "show", "--resource-group", rg, "--name", aks_cluster,
         "--query", "provisioningState", "-o", "tsv"]
    )
    if aks_status:
        print(f"  Status: {aks_status}")
        if aks_status == "Succeeded":
            print("  AKS cluster is ready for deployment")
    else:
        print("  Status: Not found or not ready")
    return True


def _preflight() -> None:
    """Anchor cwd to the script folder so `az acr build ... api/` always resolves."""
    script_dir = Path(__file__).resolve().parent
    dockerfile = script_dir / "api" / "Dockerfile"
    if not dockerfile.is_file():
        print("Error: 'api/Dockerfile' is missing next to azdeploy.py. "
              "Make sure you kept the exercise folder intact.")
        sys.exit(1)
    os.chdir(script_dir)


def main() -> None:
    _preflight()
    user_object_id = require_az_login()
    acr_name, aks_cluster = _derived_names(user_object_id)

    while True:
        show_menu(acr_name, aks_cluster)
        choice = input("Please select an option (1-7): ").strip()

        if choice in {"1", "2", "3", "4", "5", "6", "7"}:
            clear_screen()

        if choice == "1":
            print()
            if create_resource_group():
                print()
                create_acr(acr_name)
            print()
            pause()
        elif choice == "2":
            print()
            build_and_push_image(acr_name)
            print()
            pause()
        elif choice == "3":
            print()
            create_aks_cluster(acr_name, aks_cluster)
            print()
            pause()
        elif choice == "4":
            print()
            check_deployment_status(acr_name, aks_cluster)
            print()
            pause()
        elif choice == "5":
            print()
            deploy_to_aks(acr_name, aks_cluster)
            print()
            pause()
        elif choice == "6":
            print()
            delete_failed_aks_deployment(aks_cluster)
            print()
            pause()
        elif choice == "7":
            print("Exiting...")
            clear_screen()
            sys.exit(0)
        else:
            print("Invalid option. Please select 1-7.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
