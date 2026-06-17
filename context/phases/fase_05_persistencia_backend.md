# Fase 5 - Persistencia backend inicial

## Objetivo

Evitar que los movimientos manuales cargados desde la UI se pierdan al reiniciar la API.

## Alcance

- Persistencia JSON local en backend.
- Repository de movimientos con lectura/escritura en `backend/data/movimientos.json`.
- Carpeta `backend/data/` preparada y versionada con `.gitkeep`.
- Archivo de datos reales ignorado por Git.
- Test de persistencia y recarga del repository.

## Tareas realizadas

- Actualizado `backend/src/repositories/movimientos.repository.js`.
- Agregado `backend/tests/movimientos.repository.test.js`.
- Agregada carpeta `backend/data/`.
- Actualizado `.gitignore` para ignorar datos locales.

## Pendientes

- Definir si la persistencia local queda solo para desarrollo o si sera cache auxiliar en produccion.
- Agregar backups o rotacion si se usa en entorno real.
- Reemplazar o complementar con ASA9/ODBC cuando se avance integracion real.

## Riesgos

- JSON local no es una base transaccional.
- No hay concurrencia real: varias instancias de backend escribiendo el mismo archivo pueden pisarse.
- No guardar datos sensibles en archivos versionados.

## Proxima fase

Fase 6 - Preparacion ASA9 ODBC 32-bit desde backend.
