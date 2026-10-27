# Guía: instalar Azure CLI y entrar en la cuenta del lab

Pensada para compañeros del curso (Linux/Mint/Ubuntu; notas para Windows y macOS). Si `az login` da error de certificado, ve al apéndice final. Sin credenciales: usa las que te dé la plataforma de labs.

## 1. Instalar Azure CLI (Ubuntu / Linux Mint)

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az version
```

Si el script termina sin instalar nada (en Mint ocurre a veces), el repo de Microsoft ya queda añadido y basta con:

```bash
sudo apt-get update && sudo apt-get install -y azure-cli
```

Windows: `winget install -e --id Microsoft.AzureCLI`. macOS: `brew install azure-cli`.

## 2. Tus credenciales del lab

La plataforma da un **usuario** y un **Temporary Access Pass (TAP)**. El TAP **no es una contraseña**: `az login -u … -p …` falla con `AADSTS50126`. Solo funciona en el login interactivo del navegador. Las credenciales caducan (el lab dura ~120 min).

## 3. Login con la cuenta del lab

```bash
az logout            # limpia sesiones previas
az login --use-device-code
```

1. Abre `https://microsoft.com/devicelogin` en una **ventana de incógnito** (así no se mezcla con tu cuenta personal o corporativa).
2. Pega el código que muestra la terminal.
3. Cuando pregunte la cuenta: **"Usar otra cuenta"** → escribe el usuario del lab.
4. En "Otras formas de iniciar sesión" elige **Temporary Access Pass** y pega el TAP.
5. La terminal imprime la suscripción del lab. Si no la imprime, el login no se completó.

Errores típicos:
- Entrar con tu cuenta personal: `az account show` dice "Please run 'az login'" o no hay suscripciones.
- TAP ya usado o caducado: pide uno nuevo en la plataforma.
- Comprueba siempre qué cuenta usa `az`: `az account show -o table` (el nombre de suscripción debe ser el del lab).

## 4. Verificación rápida

```bash
az account show -o table
az group list -o table        # vacío en un lab recién creado
az provider show -n Microsoft.ContainerRegistry --query registrationState -o tsv
```

## Apéndice · Error de certificado (solo si tu red tiene un proxy que intercepta TLS)

No aplica a la mayoría de redes domésticas. Solo si `az login` falla con el error siguiente.

Síntoma al hacer `az login`:

```
SSLCertVerificationError ... self-signed certificate in certificate chain
```

Causa: la red de la empresa tiene un proxy que intercepta TLS (p. ej. Netskope) y re-firma los certificados con su propia CA. El sistema operativo ya confía en esa CA, pero `az` usa su propio bundle de Python y no.

Solución: decirle a `az` que use el almacén de certificados del sistema. **No desactives la verificación TLS.**

Para comprobar que es tu caso, mira quién emite el certificado:

```bash
echo | openssl s_client -connect login.microsoftonline.com:443 2>/dev/null | grep 'i:'
```

Si el emisor no es Microsoft/DigiCert sino el de tu empresa, es el proxy.

**Linux**

```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# permanente:
echo 'export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt' >> ~/.bashrc
```

**Windows (PowerShell)** — exporta la CA del proxy:
1. `certmgr.msc` → *Entidades de certificación raíz de confianza* → certificados → busca el de tu proxy (p. ej. `goskope` / `Netskope`).
2. Clic derecho → *Todas las tareas* → *Exportar…* → formato **Base-64 (.cer)** → guarda como `C:\certs\proxy-ca.pem`.
3. `setx REQUESTS_CA_BUNDLE "C:\certs\proxy-ca.pem"` y abre una terminal nueva.

Si el fichero solo contiene la CA del proxy, `az` dejará de confiar en el resto; en ese caso concaténala al final de `certifi`: ruta con `az --version` (línea *Python location*) y `python -c "import certifi;print(certifi.where())"` con ese Python.

**macOS**

```bash
security find-certificate -a -p /Library/Keychains/System.keychain /System/Library/Keychains/SystemRootCertificates.keychain > ~/proxy-bundle.pem
export REQUESTS_CA_BUNDLE=~/proxy-bundle.pem
```

Si no sabes de dónde sacar la CA, pídesela al equipo de IT/seguridad: es un certificado público de la empresa, no un secreto.
