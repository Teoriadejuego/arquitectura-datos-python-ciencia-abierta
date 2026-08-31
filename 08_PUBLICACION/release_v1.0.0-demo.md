# Borrador de release `v1.0.0-demo`

**Estado:** DEMOSTRACIÓN DOCENTE · NO PUBLICADO  
**Fecha prevista:** 2026-09-02  
**Autor:** Antonio Alfonso

## Título

La velocidad de las frutas: datos sintéticos y materiales reproducibles para
docencia

## Contenido de esta versión

- Conjunto público de 500 registros generados por código, siempre identificado
  como `sintetico_docente`.
- Regla analítica mecánica que excluye 20 filas con algún tiempo menor que
  2,0 segundos y conserva exactamente 2,00 segundos; quedan 480 filas válidas,
  240 por orden.
- Esquemas, diccionario y metadatos para comprobar el contrato público.
- Scripts reproducibles, cuaderno ejecutado y resultados calculados.
- Miniweb local de demostración, protocolo docente y activos visuales.
- Archivos de cita, licencias y metadatos preparados para Zenodo Sandbox.

## Alcance de publicación

El release público debe construirse mediante una lista positiva. Puede incluir:

- `04_DATOS/sinteticos_raw/`, porque fue generado íntegramente por código y
  permite reproducir la transformación; esta excepción nunca se aplica a datos
  brutos procedentes de personas;
- `04_DATOS/publicos/`;
- esquemas, diccionario y metadatos publicables de `04_DATOS/metadata/`;
- código y documentación sin secretos, bajo MIT;
- resultados agregados y figuras rotuladas `SIMULACIÓN DOCENTE`, bajo CC BY 4.0;
- protocolo y materiales docentes revisados, bajo CC BY 4.0;
- los archivos de `08_PUBLICACION/` pertinentes al paquete.

Nunca debe incluir:

- datos brutos reales ni `04_DATOS/restringidos/`;
- mapas de bonificación, emparejamientos o pagos;
- SQLite, secretos o ficheros `.env`;
- IDs de plataforma, HMAC, texto abierto o timestamps exactos;
- cachés, entornos virtuales o artefactos temporales.

El depósito de datos curado descrito por `zenodo_sandbox_metadata.json` es más
estrecho: contiene únicamente el CSV público, sus metadatos y los resultados
publicables bajo CC BY 4.0. El código MIT permanece como componente separado del
release y no debe incluirse en un depósito cuyo campo único de licencia sea
CC BY 4.0.

Si se usa la integración automática GitHub–Zenodo, Zenodo archivará el release
completo del repositorio. En ese caso también viajarán el código y la capa bruta
sintética; antes de publicarlo deben revisarse el alcance de la licencia y los
metadatos del registro completo.

## Resultados de referencia

Los resultados son deliberadamente sintéticos. El análisis principal usa solo
la primera decisión: media 89,25 km/h para naranja primero y 68,67 km/h para
plátano primero; Welch unilateral `t = 13,964`, `p ≈ 1,216 × 10⁻³⁷` y
`d = 1,275`. Estas cifras sirven para enseñanza y no constituyen evidencia sobre
seguridad vial, comprensión intercultural o preferencias universales.

## Integridad y licencias

- CSV público: SHA-256
  `59a4e0b4794e6fcb8782c831ac207d0e5867ce3cc803c184414c5441d4f15a41`.
- Código propio: MIT, según `LICENSE_CODIGO.txt`.
- Datos públicos sintéticos, metadatos, resultados y materiales docentes
  propios: CC BY 4.0, según `LICENSE_DATOS.txt`.
- Materiales de terceros: conservan sus licencias y requieren revisión antes de
  cualquier inclusión.

## Estado de depósito

- No se ha creado un DOI ni se ha reservado ninguno.
- No se ha añadido un ORCID porque no se proporcionó uno.
- `zenodo_sandbox_metadata.json` es una plantilla local para
  `https://sandbox.zenodo.org/`; no se ha enviado.
- `.zenodo.json` es una copia compatible de los metadatos esenciales y se
  mantiene fuera de la raíz del repositorio para evitar activación accidental.
- No se ha creado ni publicado un release en GitHub.

## Lista de comprobación previa a una demostración

- [ ] Regenerar todos los productos desde una carpeta limpia.
- [ ] Verificar el manifiesto SHA-256 del paquete público.
- [ ] Confirmar la lista positiva y la ausencia de datos restringidos.
- [ ] Revisar que las licencias coinciden con cada componente.
- [ ] Crear solo un borrador en Zenodo Sandbox.
- [ ] Detenerse antes de **Publish**.
