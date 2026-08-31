# Publicación de demostración

Esta carpeta prepara los metadatos y avisos legales de **La velocidad de las
frutas** para la versión `v1.0.0-demo`, con fecha 2026-09-02 y autor Antonio
Alfonso.

Todo permanece local. Los archivos no acreditan una publicación, un DOI, una
reserva de DOI ni un depósito. Si se realiza la práctica, debe utilizarse
exclusivamente [Zenodo Sandbox](https://sandbox.zenodo.org/) y detenerse antes
de **Publish**.

## Archivos

| Archivo | Función |
|---|---|
| `CITATION.cff` | Cita CFF 1.2.0 del conjunto público sintético. No contiene DOI, ORCID ni URL de repositorio inventada. |
| `LICENSE_CODIGO.txt` | Licencia MIT del código propio. |
| `LICENSE_DATOS.txt` | CC BY 4.0 para datos, metadatos, resultados y materiales públicos propios; delimita exclusiones. |
| `release_v1.0.0-demo.md` | Notas de release en estado borrador y lista positiva de contenido. |
| `zenodo_sandbox_metadata.json` | Cuerpo local de metadatos con envoltura `metadata`, apto para una demostración de la API de depósitos en Sandbox. |
| `.zenodo.json` | Metadatos equivalentes para una eventual integración GitHub–Zenodo, conservados aquí como plantilla inerte. |

## Dos licencias, dos alcances

El código propio usa MIT. El CSV público sintético, sus metadatos, resultados y
materiales docentes propios usan CC BY 4.0. Las capas bruta y restringida no
tienen licencia pública cuando proceden de participantes. La capa
`sinteticos_raw` de este curso es una excepción documentada: fue generada por
código, no contiene personas y puede compartirse para reproducir el pipeline.

Zenodo documenta que el campo `license` de un depósito abierto se aplica a
todos sus archivos. Por ello la plantilla Sandbox describe un depósito de datos
curado bajo CC BY 4.0 y excluye el código MIT. La licencia de cada componente no
debe homogeneizarse para facilitar una carga.

## Sobre `.zenodo.json` y `CITATION.cff`

Zenodo admite ambos formatos para releases procedentes de GitHub, pero si los
dos están en la raíz del repositorio utiliza `.zenodo.json` e ignora por completo
`CITATION.cff` durante el archivado. En este proyecto ambos son coherentes en
título, autor, versión, fecha, tipo y licencia de datos. La plantilla
`.zenodo.json` permanece en `08_PUBLICACION/`, no en la raíz, para evitar una
integración accidental.

Solo debería copiarse a la raíz después de revisar que el release que Zenodo va
a archivar contiene exclusivamente el payload público descrito y que no crea un
conflicto de licencias.

## Lista positiva del depósito Sandbox

Puede contener:

- `04_DATOS/publicos/velocidad_frutas_publico.csv`;
- `04_DATOS/metadata/schema_publico.json`;
- `04_DATOS/metadata/diccionario_datos.csv`;
- `04_DATOS/metadata/metadata_dataset.json`;
- resultados agregados y figuras publicables rotulados `SIMULACIÓN DOCENTE`;
- `CITATION.cff`, `LICENSE_DATOS.txt`, las notas de release y la documentación
  de reproducción correspondiente.

No puede contener:

- datos brutos reales ni `04_DATOS/restringidos/`;
- mapas de bonificación, emparejamientos o pagos;
- SQLite, secretos, `.env`, IDs de plataforma o HMAC;
- texto abierto, timestamps exactos, cachés o entornos virtuales;
- código MIT dentro del depósito descrito como CC BY 4.0;
- ningún archivo real de participantes.

## Validación local

Validación completa de CFF 1.2.0 mediante el validador oficial de referencia:

```powershell
uvx --from cffconvert cffconvert --validate '08_PUBLICACION/CITATION.cff'
```

Validación sintáctica de ambos JSON con la biblioteca estándar de Python:

```powershell
py -3.12 -m json.tool '08_PUBLICACION/zenodo_sandbox_metadata.json' > $null
py -3.12 -m json.tool '08_PUBLICACION/.zenodo.json' > $null
```

La coherencia cruzada también debe comprobar que:

- título, versión, fecha y autor coinciden en los tres formatos;
- el tipo es `dataset` y la licencia de datos es CC BY 4.0;
- no aparecen claves `doi` u `orcid`;
- no se usa `zenodo.org` de producción ni se envía ninguna petición.

## Flujo docente seguro

1. Regenerar el paquete público desde una carpeta limpia.
2. Verificar el manifiesto y la lista positiva.
3. Abrir solo `https://sandbox.zenodo.org/`.
4. Crear un borrador y copiar los metadatos locales.
5. Revisar archivos, autor, fecha, versión y licencia.
6. Detenerse antes de **Publish** y borrar el borrador al terminar si ya no se
   necesita.

La integración automática GitHub–Zenodo sigue otra frontera: archiva la
instantánea completa del release de GitHub. Este repositorio público puede
usarse porque solo contiene datos sintéticos y archivos revisados. No debe
reutilizarse la misma operación con un repositorio que contenga datos reales o
material restringido.

No se debe pasar a Zenodo de producción para resolver un problema de la
demostración.

## Referencias oficiales

- [Citation File Format: guía del esquema 1.2.0](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md).
- [cffconvert: validador oficial de CFF](https://github.com/citation-file-format/cffconvert).
- [Zenodo: formato `.zenodo.json`](https://help.zenodo.org/docs/github/describe-software/zenodo-json/).
- [Zenodo Developers: metadatos de depósitos](https://developers.zenodo.org/#deposit-metadata).
- [Zenodo: inicio rápido y entorno Sandbox](https://help.zenodo.org/docs/get-started/quickstart/).
- [Open Source Initiative: texto MIT](https://opensource.org/license/mit).
- [Creative Commons: CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).
- [Creative Commons: código legal CC BY 4.0 en español](https://creativecommons.org/licenses/by/4.0/legalcode.es).
