# Aviso de terceros

> **Repositorio de formación.** Los labs de este repositorio son material de un curso y se ejecutaron en entornos temporales (cuentas y suscripciones de laboratorio ya destruidas). Los `.env`, nombres de recursos y endpoints que se versionan en `labs/` proceden de esos entornos desechables y no contienen claves.

Los ficheros de partida de los labs (`azdeploy.py`, carpeta `api/`, `document.txt`) proceden del repositorio de Microsoft [MicrosoftLearning/mslearn-azure-ai](https://github.com/MicrosoftLearning/mslearn-azure-ai), publicado bajo licencia MIT (Copyright (c) 2024 Microsoft). Se incluyen sin modificar, salvo los valores que el propio lab indica editar (nombre del resource group, región y SKU), para estudiar y reproducir los labs.

Texto de la licencia: https://github.com/MicrosoftLearning/mslearn-azure-ai/blob/main/LICENSE

Se incluyen también los zips originales del lab. Se versionan los `.env` generados por los scripts (sin claves; los que las contienen siguen ignorados), pero no los zips duplicados del curso. Las presentaciones y knowledge check del curso (públicos) viven en `docs/`.

`labs/lp3-01-aks-deploy/aks-deploy-python-plataforma.zip` es la variante del mismo starter que distribuye la plataforma de laboratorios del curso (misma procedencia MicrosoftLearning/mslearn-azure-ai, con cuatro valores de configuración añadidos al principio de `azdeploy.py`); se conserva sin editar para poder reproducir el lab.
