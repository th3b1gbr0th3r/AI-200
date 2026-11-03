#!/usr/bin/env bash
# Rellena los cuatro valores de azdeploy.py (Task 3-4 de la plataforma) con consultas az de SOLO LECTURA.
# Uso:  ./configurar.sh <resource-group> [salida]
#   <resource-group>  grupo de la plataforma donde está el proyecto de Foundry (az group list -o table)
#   [salida]          fichero a generar (por defecto azdeploy.py). Parte siempre del azdeploy.py ORIGINAL del zip.
set -euo pipefail
RG="${1:?Uso: $0 <resource-group> [salida]}"
OUT="${2:-azdeploy.py}"
cd "$(dirname "$0")"
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

LOC=$(az group show -n "$RG" --query location -o tsv)
FND=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices']|[0].name" -o tsv)
[ -n "$FND" ] || { echo "No hay recurso AIServices en $RG: falta el Task 1 (proyecto de Foundry)"; exit 1; }
EP=$(az cognitiveservices account show -g "$RG" -n "$FND" --query "properties.endpoints.\"Azure OpenAI Legacy API - Latest moniker\"" -o tsv)
DEP=$(az cognitiveservices account deployment list -g "$RG" -n "$FND" --query "[0].name" -o tsv)
[ -n "$EP" ] && [ -n "$DEP" ] || { echo "Falta endpoint OpenAI o despliegue del modelo (Task 2)"; exit 1; }

unzip -p aks-deploy-python-plataforma.zip azdeploy.py \
 | sed "s|YOUR_RESOURCE_GROUP|$RG|; s|YOUR_REGION|$LOC|; s|YOUR_FOUNDRY_ENDPOINT|$EP|; s|YOUR_DEPLOYMENT_NAME|$DEP|" > "$OUT"
echo "Generado $OUT con: rg=$RG location=$LOC deployment=$DEP (endpoint de $FND)"
grep -c "YOUR_" "$OUT" | sed 's/^/Placeholders YOUR_ restantes: /'
