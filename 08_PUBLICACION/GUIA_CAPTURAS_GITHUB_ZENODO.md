# Guía de capturas: Git, GitHub, release y Zenodo

La demostración debe realizarse con este repositorio público y con datos sintéticos. No active ningún estudio real de Prolific.

## 1. Historia local

Capture la terminal después de ejecutar:

```powershell
git status --short
git log --oneline --decorate --graph --all
git show --stat HEAD
```

La imagen debe mostrar commits con una decisión reconocible. Evite una captura que revele rutas personales, correos no deseados o tokens.

## 2. Repositorio de GitHub

Después de crear un repositorio público vacío en GitHub:

```powershell
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

Capturas recomendadas:

1. Página principal: README, carpetas y rótulo de simulación visibles.
2. Historial: enlace `commits` y mensajes atómicos.
3. Un commit: pestaña `Files changed`.
4. Archivo `CITATION.cff`: botón `Cite this repository` si GitHub lo muestra.

## 3. Release de demostración

Antes del release:

```powershell
git status --short
git tag -a v1.0.0-demo -m "Versión pública del curso"
git push origin v1.0.0-demo
```

En GitHub, cree un release desde ese tag. Use el título `v1.0.0-demo · simulación docente`. No adjunte bases locales ni carpetas restringidas.

Capture:

1. Selector del tag.
2. Notas del release.
3. Release publicado con la etiqueta visible.

## 4. Integración con Zenodo

1. Vincule la cuenta de GitHub desde Zenodo.
2. Abra la sección GitHub de Zenodo.
3. Sincronice la lista y habilite este repositorio.
4. Cree el release en GitHub o espere a que Zenodo procese el ya publicado.
5. Abra el registro generado y compruebe título, autoría, licencia, versión y archivos.

Capture:

1. Repositorio habilitado en Zenodo.
2. Release en proceso o archivado.
3. Página del registro y DOI de versión.
4. Apartado de versiones, si aparece.

Zenodo archiva la instantánea del release. GitHub conserva el desarrollo y su historial. El DOI identifica el objeto depositado; no certifica la calidad del análisis.

## 5. Si solo se desea ensayar

Use Zenodo Sandbox para practicar los formularios sin crear el registro definitivo. Un DOI o URL de Sandbox debe presentarse siempre como demostración, no como depósito científico publicado.
