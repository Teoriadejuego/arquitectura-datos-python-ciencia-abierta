# Prolific · Configuración del estudio

> # BORRADOR — NO PUBLICAR
>
> No pulsar **Publish**, no reservar plazas y no transferir presupuesto. Este documento configura una demostración. La recogida del curso será sintética.

**Verificación de documentación oficial:** 28 de agosto de 2026  
**Tipo:** External Study Link  
**Aplicación:** miniweb Streamlit alojada externamente  
**Duración estimada:** 4 minutos  
**Muestra principal:** 500 envíos completos  
**Estado:** borrador local; no existe estudio activo

---

## 1. Resumen de configuración

| Campo de Prolific | Valor del borrador |
|---|---|
| Internal name | `[BORRADOR] Velocidad de símbolos · ES · desktop · v1` |
| Study title | `Cómo interpretamos símbolos nuevos` |
| Data collection | `External Study Link` |
| Estimated completion time | `4 minutes` |
| Reward | `£0.60` por envío completo |
| Hourly rate | `£9.00/hour` |
| Places | `500` |
| Distribution | `Standard sample` |
| Countries | `All available countries` |
| Language | `Fluent languages: Spanish` |
| Age | `18 years or older` |
| Device | Portátil o escritorio; no móvil ni tableta |
| Driving licence | Custom screening salvo filtro integrado exacto |
| Submissions per participant | `Once` |
| Review | Manual durante piloto y primera ejecución |
| Completion | Redirección automática después del guardado |
| Automatic fast rejection | Desactivado para la regla docente `< 2.0 s` |

No se selecciona muestra representativa. La inferencia se limita a voluntarios elegibles de Prolific que comprenden español y completan la tarea en ordenador.

---

## 2. Título y descripción visibles

### Título

```text
Cómo interpretamos símbolos nuevos
```

El título no revela la dirección naranja–plátano ni promete una respuesta correcta.

### Descripción breve

```text
Tarea de cuatro minutos en español sobre la interpretación de dos símbolos
ficticios. Elegirá una velocidad y una confianza para cada símbolo. Debe tener
18 años o más, un permiso de conducir vigente y utilizar un ordenador portátil
o de escritorio. No participe mientras conduce. No se pedirá el número ni una
copia de su permiso. Incluye una explicación final opcional.
```

### Resumen de datos para participantes

```text
La aplicación recibe los identificadores técnicos que Prolific añade a la URL
para enlazar el envío y tramitar pagos. Se guardan de forma restringida y se
seudonimizan mediante HMAC. El texto final es opcional: no escriba nombres ni
información personal. Consulte la hoja de información antes de consentir.
```

---

## 3. Enlace externo e identificadores

### URL base que se pega en Data collection

```text
https://[DOMINIO_PUBLICO_DE_LA_APP]/?modo=docente
```

Seleccionar **I'll use URL parameters**. Prolific recomienda registrar los IDs mediante parámetros y añade `PROLIFIC_PID`, `STUDY_ID` y `SESSION_ID`. El patrón final que debe mostrar la previsualización es:

```text
https://[DOMINIO_PUBLICO_DE_LA_APP]/?modo=docente
  &PROLIFIC_PID={{%PROLIFIC_PID%}}
  &STUDY_ID={{%STUDY_ID%}}
  &SESSION_ID={{%SESSION_ID%}}
```

En la URL real no hay saltos de línea. La aplicación:

1. captura los tres parámetros;
2. rechaza cadenas vacías o mal formadas;
3. conserva los IDs brutos solo en la capa restringida;
4. genera HMAC con secreto externo;
5. usa `SESSION_ID` para idempotencia y enlace local con la exportación;
6. nunca escribe IDs o HMAC en logs públicos.

Si el workspace ofrece **Secure external URL**, solo se activará cuando la aplicación pueda validar el JWT según la documentación de Prolific. Activarlo sin validar el token bloquearía accesos legítimos. La disponibilidad está limitada a ciertos workspaces.

---

## 4. Completion paths

### Finalización correcta

Crear una ruta **Completed study** con revisión manual y copiar la URL generada:

```text
https://app.prolific.com/submissions/complete?cc=[CODIGO_COMPLETO_GENERADO]
```

Variable de despliegue de la app:

```text
PROLIFIC_COMPLETION_URL=https://app.prolific.com/submissions/complete?cc=[CODIGO_COMPLETO_GENERADO]
```

La redirección ocurre si, y solo si, la escritura final se confirma. Prolific recomienda la redirección automática; el código nunca se muestra antes del guardado.

### Sin consentimiento

Crear **No consent → Request a return**:

```text
[URL_NO_CONSENTIMIENTO_GENERADA_POR_PROLIFIC]
```

No consentir no es causa de rechazo.

### Dispositivo incompatible

Crear **Incompatible device → Request a return**:

```text
[URL_DISPOSITIVO_INCOMPATIBLE_GENERADA_POR_PROLIFIC]
```

La comprobación aparece antes de la tarea.

### Custom screen-out

Si se usa el filtro de permiso, habilitar la ruta oficial de *custom screening*:

```text
[URL_SCREENED_OUT_GENERADA_POR_PROLIFIC]
```

No reutilizar el código de finalización normal. El screen-out recibe la compensación configurada y no ocupa una de las 500 plazas de envíos completos.

---

## 5. Instrucciones exactas para participantes

### Antes de abrir el estudio

```text
Este estudio está íntegramente en español y dura aproximadamente cuatro
minutos. Ábralo solo desde un ordenador portátil o de escritorio. No use móvil
ni tableta. Debe tener 18 años o más y un permiso de conducir vigente. No se le
pedirá el número, una imagen ni el país de expedición del permiso. No participe
mientras conduce.
```

### Inicio de la aplicación

```text
Imagine que conduce en un país que nunca ha visitado. En ese país, las señales
de velocidad no muestran números: muestran símbolos. Cada símbolo corresponde
a una velocidad máxima en kilómetros por hora, pero usted desconoce el código.

Dé su mejor estimación. Cuando cierre la muestra, una de sus dos respuestas
podrá compararse con la de otra persona. Si ambas coinciden exactamente para el
mismo símbolo, cada una recibirá una bonificación adicional equivalente a
0,50 €. El pago base no depende de coincidir ni de la inclusión en un análisis.
```

### Explicación final

```text
En una frase, ¿qué le hizo asociar cada símbolo con la velocidad elegida? Esta
respuesta es opcional. No incluya nombres ni información personal.
```

### Mensaje de ayuda

```text
Si la página no carga, no guarda una respuesta o no vuelve a Prolific, no repita
el estudio en otra pestaña. Tome nota del mensaje mostrado y contacte mediante
Prolific o en [CORREO_INSTITUCIONAL_DE_SOPORTE]. No cierre una página que indique
que el guardado sigue en curso.
```

---

## 6. Audiencia y filtros

### Filtros integrados verificados

| Sección | Configuración | Motivo |
|---|---|---|
| Source | Find new participants on Prolific | Muestra estándar de voluntarios. |
| Location | All available countries | No se afirma representatividad nacional. |
| Age | 18 o más | Población adulta. |
| Fluent languages | Spanish | Instrumento íntegramente en español. |
| Study distribution | Standard sample | Custom screening no se combina con muestra representativa. |
| Submissions | Once | Una oportunidad por participante. |

El filtro **Fluent languages: Spanish** selecciona fluidez declarada; no equivale a lengua materna. No se añade país como sustituto del idioma.

### Dispositivo

En **Study details**, declarar compatibles únicamente portátil/escritorio y repetirlo en la descripción. La guía vigente indica que Prolific no restringe automáticamente el dispositivo; la aplicación validará al principio:

```text
¿Qué dispositivo está utilizando ahora?
[ ] Ordenador portátil
[ ] Ordenador de escritorio
[ ] Tableta
[ ] Teléfono móvil
[ ] Otro
```

Portátil/escritorio continúa. El resto recibe la ruta **Incompatible device → Request a return**. No se rechaza automáticamente.

### Permiso de conducir

La documentación pública consultada no confirma un prescreener integrado exacto para «permiso de conducir vigente». Antes de ejecutar:

1. buscar en **Prescreen participants → Add screeners** los términos oficiales `driving licence` y `driver's license`;
2. si existe una pregunta que mida exactamente vigencia, seleccionar la respuesta equivalente a «sí» y conservar su redacción;
3. si no existe —configuración asumida por este borrador— usar el *custom screening* oficial descrito abajo;
4. no confundir la verificación de identidad de Prolific con tener permiso: una licencia es solo uno de varios documentos que la plataforma puede aceptar.

No se solicita número, imagen, país, categoría, puntos o infracciones.

---

## 7. Custom screening para permiso vigente

### Configuración en Prolific

```text
Custom screening: Yes
Screen-out slots: 100 inicialmente
Screen-out reward: £0.10
Eligible submissions requested: 500
```

Los 100 slots son una cota inicial de borrador; el piloto debe estimar la proporción excluida. Al alcanzarse la cota, Prolific puede pausar el estudio. El reward de £0.10 es el mínimo oficial vigente para screen-outs en GBP y no puede cambiarse después de publicar.

### Pregunta al inicio

Antes de mostrar frutas:

```text
¿Cuál describe su situación actual respecto a permisos para conducir vehículos
a motor?

[ ] Tengo un permiso de conducir vigente.
[ ] Tuve un permiso, pero actualmente no está vigente.
[ ] Nunca he tenido un permiso de conducir.
[ ] Prefiero no responder.
```

Solo la primera opción continúa. Las demás llevan a la ruta *screened out*. La pregunta es obligatoria, no solicita documento y no se usa como resultado analítico.

Si el filtro integrado existe y se valida dentro del estudio, copiar **exactamente** su redacción y opciones. La guía oficial advierte que una redacción distinta puede generar discrepancias injustas. No se rechaza a alguien únicamente por una discrepancia; se usa la ruta de retorno y, si persiste el caso, soporte de Prolific.

---

## 8. Muestra, pago y coste

### Base

```text
N = 500
tiempo = 4 minutos
reward por envío = £0.60
tarifa mostrada = £9.00/h
```

Cálculo:

```text
£0.60 × 60 / 4 = £9.00/h
500 × £0.60 = £300.00 en rewards base
```

La tarifa oficial mínima vigente es £6/h y Prolific recomienda £9/h. El borrador adopta la recomendada. El pago es fijo: una persona que tarda menos no cobra menos; si la mediana real supera cuatro minutos, se aumenta la remuneración o se corrige la estimación para mantener al menos £9/h.

### Costes de plataforma orientativos

| Cuenta | Rewards base | Fee indicado por Prolific | Subtotal antes de VAT |
|---|---:|---:|---:|
| Academia / non-profit elegible | £300,00 | 33,3 % = £99,90 | £399,90 |
| Corporate | £300,00 | 42,8 % = £128,40 | £428,40 |

VAT puede aplicarse a la tarifa de plataforma, no a los rewards. El presupuesto definitivo debe tomarse del quote de Prolific, porque tipo de cuenta, VAT, screen-outs y bonus cambian el total.

Con 100 slots a £0.10, la exposición máxima adicional de rewards por *screen-out* es £10,00 más la tarifa aplicable. Los filtros integrados no añaden un coste de prescreening.

### Bonificación de coordinación

El incentivo docente es `0,50 €` por participante que coincida. Prolific opera workspaces en GBP o USD y paga en la moneda del estudio. Antes de una ejecución real:

1. fijar una fuente y fecha de cambio EUR→GBP;
2. convertir `0,50 €` a GBP;
3. redondear al céntimo superior para no pagar menos del equivalente comunicado;
4. registrar el importe convertido antes de publicar;
5. reservar por separado el máximo de 500 bonos, además del presupuesto base.

Los bonos reciben tarifa de plataforma y nunca cuentan para alcanzar el mínimo horario. El resultado sintético esperado de 166 bonos y 83,00 € es una simulación, no un presupuesto pagado.

**Este borrador no reserva fondos.** Prolific reserva el coste de la muestra cuando se publica; no se realizará ese paso.

---

## 9. Revisión de envíos y fallos

- Seleccionar revisión manual en el piloto y la primera ejecución.
- No usar la regla analítica `< 2.0 s` como rechazo o reducción de pago.
- Desactivar cualquier rechazo automático basado en esa frontera docente.
- Un `NOCODE` o código incorrecto no vuelve inválido un envío por sí solo. Si la aplicación confirma respuesta completa, revisar y aprobar conforme a la guía oficial.
- Sin consentimiento: **Request a return**, nunca rechazo.
- Dispositivo incompatible detectado al inicio: **Request a return**.
- Screen-out del permiso: usar la ruta y pago de *custom screening*.
- Fallo de almacenamiento: no redirigir; mostrar soporte y conservar idempotencia.
- Duplicado técnico del mismo `SESSION_ID`: restaurar el registro existente, no crear otro.
- No pedir al participante que repita en otra pestaña.
- Resolver dudas por mensajería de Prolific; no solicitar datos personales por correo.

Contacto del estudio visible en Prolific y la app:

```text
[CORREO_INSTITUCIONAL_DE_SOPORTE]
```

Tiempo de respuesta comprometido durante una ejecución: un día laborable.

---

## 10. Previsualización y piloto

### Preview técnico

Ejecutar **Preview** de extremo a extremo y comprobar:

1. parámetros `PROLIFIC_PID`, `STUDY_ID` y `SESSION_ID` recibidos;
2. consentimiento y rutas de salida;
3. dispositivo incompatible;
4. ambos órdenes experimentales;
5. escritura atómica e idempotente;
6. debriefing posterior;
7. redirección solo después del guardado;
8. completion code correcto.

### Piloto separado

Crear, pero no publicar durante el seminario, un borrador duplicado:

```text
N piloto = 10
reward = £0.60
review = manual
screen-out slots = 5
screen-out reward = £0.10
```

Los diez pilotos no se mezclan con los 500 casos principales. Antes del estudio principal se añaden a una blocklist o grupo excluido.

Criterios de paso:

- 10/10 sesiones enlazadas por `SESSION_ID`;
- 10/10 guardados únicos y completos;
- ambos órdenes observados;
- cero IDs en logs públicos;
- rutas de consentimiento, screen-out y dispositivo correctas;
- 10/10 redirecciones o incidencias explicadas;
- mediana compatible con cuatro minutos;
- texto de soporte y debriefing legibles en portátil/escritorio.

Un cambio sustantivo tras el piloto se registra como desviación o produce una nueva versión antes del lanzamiento.

---

## 11. Checklist de borrador

### Estudio

- [x] Tipo External Study Link.
- [x] Título neutral y descripción en español.
- [x] N=500; una submission por participante.
- [x] Tiempo=4 minutos; reward=£0.60; £9/h.
- [x] Standard sample; todos los países disponibles.
- [x] Edad 18+ y español fluido.
- [x] Portátil/escritorio declarados.
- [x] Custom screening preparado para permiso vigente.
- [ ] Confirmar en la interfaz si existe filtro integrado exacto de permiso.

### Aplicación

- [ ] Sustituir `[DOMINIO_PUBLICO_DE_LA_APP]`.
- [ ] Sustituir completion y screen-out URLs.
- [ ] Completar correo institucional y contactos éticos.
- [ ] Verificar HMAC y secreto externo.
- [ ] Implementar o descartar Secure external URL según disponibilidad/JWT.
- [ ] Ejecutar pruebas de dispositivo, idempotencia y almacenamiento.
- [ ] Verificar que no se mezclen respuestas recibidas y sintéticas.

### Ética y pagos

- [ ] Resolución institucional previa a personas reales.
- [ ] DMP y consentimiento aprobados.
- [ ] Confirmar moneda GBP del workspace.
- [ ] Congelar conversión del bono de 0,50 €.
- [ ] Obtener quote con fees, VAT, screen-outs y bonus.
- [ ] Ejecutar preview y piloto.
- [ ] Revisar soporte y plan de incidencias.

### Bloqueo final

- [x] Estado declarado **BORRADOR**.
- [x] Sin presupuesto reservado.
- [x] Sin estudio publicado.
- [ ] **Publish** permanece sin pulsar.

---

## 12. Fuentes oficiales verificadas

- [Prolific IDs y parámetros de URL](https://researcher-help.prolific.com/en/articles/445133-what-are-prolific-ids-and-how-do-i-use-them): IDs automáticos, recomendación de URL parameters y Secure external URL.
- [Compatibilidad de software y completion URL](https://researcher-help.prolific.com/en/articles/445178-what-survey-experimental-software-is-compatible-with-prolific): enlace anónimo, captura de IDs, guardado antes de redirigir y revisión de `NOCODE`.
- [Data collection](https://researcher-help.prolific.com/en/articles/445127-data-collection): External Study Link, custom screening y completion paths.
- [Modelo de pago](https://researcher-help.prolific.com/en/articles/445230-prolific-s-payment-model): reward fijo, duración estimada y mínimo/recomendación por hora.
- [Precios, fees, VAT, bonus y monedas](https://researcher-help.prolific.com/en/articles/445239-what-is-your-pricing): 33,3 % academia/non-profit, 42,8 % corporate, GBP/USD y bonus separado.
- [Custom screening](https://researcher-help.prolific.com/en/articles/445155-how-to-use-custom-screening-to-recruit-specific-participants): branching, slots, pago de screen-out y alternativa de dos estudios.
- [Recruit participants](https://researcher-help.prolific.com/en/articles/445128-recruit-participants): fuente, muestra estándar, prescreeners y una submission.
- [Screening, dispositivos y falta de consentimiento](https://researcher-help.prolific.com/en/articles/445165-can-i-screen-participants-within-my-study): validación temprana y rutas Request a return.
- [Filtro de idiomas](https://researcher-help.prolific.com/en/articles/445169-how-do-i-prescreen-for-participants-who-are-fluent-in-multiple-languages): `Fluent languages` y su lógica.
- [Previewing your study](https://researcher-help.prolific.com/en/articles/445131-previewing-your-study): prueba de IDs y finalización antes del lanzamiento.

La interfaz y las tarifas deben volver a comprobarse el día de una eventual ejecución. Este archivo no autoriza publicación, reclutamiento ni gasto.
