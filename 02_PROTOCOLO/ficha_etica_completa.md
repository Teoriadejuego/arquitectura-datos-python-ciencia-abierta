# Ficha ética y de protección de datos · Caso completado

> **SIMULACIÓN DOCENTE.** Este documento describe cómo se prepararía el estudio «La velocidad de las frutas». Los 500 registros del curso son sintéticos. La ficha no es una aprobación y no sustituye la evaluación de un comité, del responsable institucional o del delegado de protección de datos. No se reclutarán personas reales con esta versión.

## Identificación

| Campo | Valor |
|---|---|
| Proyecto | La velocidad de las frutas |
| Investigador responsable | Antonio Alfonso |
| Institución | **[COMPLETAR ANTES DE UNA RECOGIDA REAL]** |
| Comité / referencia | **[COMPLETAR; no existe aprobación en la simulación]** |
| Responsable del tratamiento | **[COMPLETAR CON LA INSTITUCIÓN COMPETENTE]** |
| Contacto de protección de datos | **[COMPLETAR CON EL DPD/DPO INSTITUCIONAL]** |
| Versión | 1.0.0-demo |
| Fecha | 28 / 08 / 2026 |

**Estado**  
[ ] Borrador real · [x] Simulación · [ ] En revisión · [ ] Aprobado · [ ] Exento

La aplicación práctica del RGPD depende del contexto institucional, la jurisdicción y la finalidad efectiva. Esta ficha no constituye asesoramiento legal. La base jurídica se determinará antes de cualquier reclutamiento real.

---

## 1. Propósito y alcance

**Pregunta:** ¿se asigna una velocidad media inicial mayor a una naranja que a un plátano cuando ambos son señales ficticias sin números?

**Tarea:** escenario hipotético, dos símbolos en orden aleatorio, seis velocidades, confianza 0–100 y explicación final opcional.

**Límite:** mide saliencia y coordinación en la tarea. No evalúa conducción, seguridad, capacidad, cumplimiento normativo ni validez universal de una señal.

[ ] Intervención física · [ ] Conducta real · [x] Escenario hipotético · [x] Decisión incentivada · [x] Texto libre opcional

---

## 2. Participantes y reclutamiento

| Elemento | Especificación simulada |
|---|---|
| Población | Personas adultas con permiso de conducir vigente y comprensión del español |
| N | 500 registros sintéticos; ninguna persona real |
| Edad mínima | 18 años |
| Inclusión | Consentimiento, permiso vigente autodeclarado, español, no estar conduciendo, sin participación previa detectable |
| Exclusión de entrada | Menor de edad, sin permiso vigente, sin consentimiento, estar conduciendo o no comprender las instrucciones |
| Canal previsto | Prolific externo, únicamente como borrador |
| Duración prevista | 4 minutos |

[x] No se reclutan menores  
[x] No se dirige a población vulnerable  
[x] No se pide el número, fotografía, país o categoría del permiso  
[x] No se recogen antecedentes, infracciones o capacidad de conducción  
[x] La persona puede abandonar antes del envío

---

## 3. Procedimiento y seguridad

1. Información, elegibilidad y consentimiento.
2. Advertencia: «No responda mientras conduce ni opera maquinaria».
3. Escenario de un país ficticio cuyas señales no muestran números.
4. Primera fruta, velocidad y confianza.
5. Segunda fruta, velocidad y confianza.
6. Explicación opcional sin datos personales.
7. Envío, debriefing y retorno a la plataforma.

[x] Señales ficticias  
[x] Sin conducción durante la tarea  
[x] Sin recomendación de conducta vial  
[x] Orden aleatorio persistente 1:1  
[x] Hipótesis revelada en el debriefing  
[x] Salida neutral para quien no consiente

**Incidencia:** no redirigir si falla el guardado; conservar el pago base cuando exista un envío aceptado; registrar el error sin exponer identificadores.

---

## 4. Riesgos y beneficios

| Riesgo | Nivel | Mitigación | Residual |
|---|---|---|---|
| Responder mientras conduce | Bajo si se sigue la instrucción | Advertencia previa y confirmación obligatoria | Bajo |
| Confusión o frustración por no existir respuesta correcta | Bajo | Escenario breve, abandono libre y debriefing | Bajo |
| Datos personales no solicitados en texto | Bajo–medio | Campo opcional, advertencia, límite y revisión; no publicar texto | Bajo |
| Enlace entre plataforma y respuesta | Bajo–medio | HMAC, separación física, mínimo acceso y borrado programado | Bajo |
| Interpretar la tarea como recomendación vial | Bajo | Rótulo ficticio y límite repetido en información y debriefing | Bajo |

**Beneficio directo:** ninguno, aparte de la remuneración.  
**Beneficio esperado:** demostrar un flujo de investigación reproducible con datos sintéticos.

Clasificación propuesta: **riesgo mínimo**, pendiente siempre de resolución institucional antes de una ejecución real.

---

## 5. Minimización y privacidad

**Necesarios en una ejecución real:** mayoría de edad sí/no, permiso vigente sí/no, consentimiento, dos velocidades, dos confianzas, dos duraciones, orden, texto opcional y parámetros mínimos de Prolific.

**No se recogen:** edad exacta, número o imagen del permiso, matrícula, IP, geolocalización, salud, infracciones, historial de conducción, teléfono o dirección.

[x] Texto abierto opcional y máximo 1.000 caracteres  
[x] Advertencia de no incluir nombres ni información personal  
[x] `PROLIFIC_PID`, `STUDY_ID` y `SESSION_ID` separados de análisis  
[x] HMAC-SHA-256 con secreto externo y dominios separados  
[x] HMAC tratado como seudónimo enlazable, no como anonimización  
[x] Timestamps exactos restringidos; análisis usa duraciones  
[x] Mapa de bonificación separado  
[x] Publicación mediante lista positiva y datos sintéticos

**Base jurídica:** no fijada en esta simulación. El consentimiento para participar no se presentará como sustituto automático de la base jurídica RGPD; la institución competente documentará la base aplicable antes del reclutamiento.

---

## 6. Almacenamiento y acceso

| Capa | Contenido | Ubicación | Acceso | Cifrado |
|---|---|---|---|:---:|
| Original sintética | Captura simulada, texto y timestamps simulados | `04_DATOS/sinteticos_raw/` | Custodio | [x] |
| Restringida simulada | HMAC y mapa de pagos simulados | Contenedor local fuera de Git | Custodio / pagos | [x] |
| Analítica | Variables derivadas sin texto ni IDs | Entorno local reproducible | Analista autorizado | [x] |
| Pública | 500 filas sintéticas y metadatos | GitHub / Zenodo Sandbox de demostración | Cualquier persona | [x] tránsito |

[x] MFA y mínimo privilegio  
[x] Accesos nominales  
[x] Copia institucional cifrada  
[x] Secreto HMAC fuera del repositorio  
[x] IDs, texto, timestamps y pagos fuera de GitHub, ZIP y Zenodo  
[x] Retención conforme al DMP

---

## 7. Consentimiento y retirada

[x] Información antes de responder  
[x] Casillas sin premarcar  
[x] Finalidad, duración, riesgos, pagos y contactos  
[x] Participación voluntaria  
[x] Retirada explicada en dos momentos  
[x] No se recuperan pagos ya realizados

**Antes de eliminar el enlace:** la persona solicita retirada por el canal institucional, aporta su referencia de participación y el custodio localiza el registro mediante la tabla restringida. Se eliminan respuesta y copias sujetas al protocolo; se conserva solo el mínimo contable que resulte obligatorio.

**Después de destruir el enlace o generar una salida irreversiblemente agregada:** ya no es posible localizar una fila individual. Esta limitación se comunica antes de consentir. La fecha de corte se fijará en la hoja de información de una ejecución real.

En el curso no existe una persona que pueda retirar datos: los 500 registros son sintéticos.

---

## 8. Pago e incentivo

| Concepto | Importe de la simulación | Condición | ¿Afecta al análisis? |
|---|---:|---|:---:|
| Pago base | 0,80 € por 4 minutos; cifra docente equivalente a 12 €/h | Envío completo aceptado; independiente de elecciones | No |
| Bonificación | 0,50 € por persona | Coincidencia exacta con la pareja en la fruta seleccionada | No |

[x] El pago base no depende de la bonificación  
[x] Una exclusión por tiempo no retira el pago base ni la opción de bonificación  
[x] El mecanismo se explica antes de responder  
[x] Emparejamiento y pagos se calculan después de cerrar la muestra  
[x] El mapa es restringido  
[x] Una retirada no exige devolver pagos

Antes de una ejecución real, el importe base se recalculará en la moneda y según la tarifa vigente de la plataforma; la bonificación nunca compensará un pago base insuficiente.

---

## 9. Publicación, derechos y contactos

**Salida pública:** solo datos sintéticos con `origen_dato=sintetico_docente`, código, esquemas, metadatos y resultados agregados.  
**Excluidos:** IDs Prolific, HMAC, timestamps exactos, `respuesta_abierta`, parejas e importes individuales.  
**Licencias:** CC BY 4.0 para material publicable; MIT para código.

En una ejecución real, las solicitudes de acceso, rectificación, supresión, limitación u oposición y la posibilidad de reclamar ante una autoridad se describirán conforme al marco aplicable y a la información aprobada por la institución. No se promete un derecho sin explicar sus posibles límites legales o técnicos.

| Contacto | Dirección / canal |
|---|---|
| Equipo investigador | **[CORREO INSTITUCIONAL POR COMPLETAR]** |
| Responsable del tratamiento | **[NOMBRE Y DIRECCIÓN INSTITUCIONAL POR COMPLETAR]** |
| Protección de datos | **[CONTACTO DPD/DPO POR COMPLETAR]** |
| Comité ético | **[COMITÉ Y REFERENCIA POR COMPLETAR]** |
| Autoridad de control | **[AUTORIDAD Y ENLACE APLICABLES POR COMPLETAR]** |

## Resolución

[ ] Aprobado · [ ] Exento · [ ] En revisión · [x] No iniciar reclutamiento real con este documento

| Función | Nombre | Firma | Fecha |
|---|---|---|---|
| Investigador responsable | Antonio Alfonso | Pendiente | 02 / 09 / 2026 |
| Revisión ética | **[COMPLETAR]** | Pendiente | — |
| Protección de datos | **[COMPLETAR]** | Pendiente | — |
