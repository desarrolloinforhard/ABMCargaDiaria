# Coding Standards

## Generales

- Codigo claro y modular.
- Evitar archivos gigantes.
- Separar responsabilidades por carpeta y capa.
- Usar nombres en espanol para dominio de negocio si corresponde.
- Usar nombres tecnicos claros para infraestructura.
- Documentar decisiones importantes.
- No hardcodear rutas ni credenciales.
- Toda conexion debe ir por configuracion externa.
- Agregar tests enfocados cuando se introduzcan modelos, services o repositories.

## Frontend Python

- Todo frontend debe basarse en TkInforHard.
- No mezclar reglas de negocio profundas en pantallas.
- No conectar directo a ASA9, ODBC ni CSV bancario.
- Consumir backend por API HTTP.
- Mantener modelos livianos para UI y adaptacion de datos.

## Backend Node.js

- Exponer contratos REST claros.
- Mantener rutas delgadas: validacion HTTP y delegacion a services.
- Mantener reglas en `services/`.
- Mantener acceso a datos en `repositories/`.
- No importar nada de TkInforHard ni frontend.
- ASA9, CSV, credenciales, logs y auditoria pertenecen al backend.

## Contratos API

- `context/api_contracts/` es la fuente comun entre frontend y backend.
- No cambiar un endpoint sin actualizar su contrato.
- Los enums de tipo, estado y origen deben mantenerse alineados en frontend/backend.
- Los montos viajan como string decimal en JSON para evitar errores de punto flotante.

## Logging

- Frontend debe usar `app.infrastructure.logging.get_logger`.
- API calls deben loguear request, response y errores con traceback.
- Errores capturados deben usar `logger.exception(...)` cuando haya excepcion activa.
- No loguear credenciales ni secretos.
- Logs locales no se versionan.
