# Actividad 003 · Reorganización catálogo Nous

## 1. Introducción

La actividad parte del escenario trabajado en clase: un catálogo de utilidades independientes de Nous. El objetivo no es solo listarlas, sino **integrarlas en suites de negocio** con mayor alcance funcional.

Para ello se desarrolla `Nous Suite Hub`, una aplicación propia que transforma módulos aislados (marketing, ERP, formación, RRHH, IA, etc.) en soluciones integradas con trazabilidad técnica y estimación de valor empresarial.

## 2. Desarrollo detallado

### 2.1 Base reutilizada desde el área de trabajo

Se toma como referencia el trabajo previo de:

- `listadodemodulos` (catálogo y categorías),
- `dashboard` (backend de datos y panel de gestión),
- documento base `001-Reorganizacion catalogo Nous.md`.

A partir de esa base, se implementa una nueva solución desde cero en Flask + SQLite.

### 2.2 Cambios funcionales de alto calado (código + base de datos)

Se crea un nuevo modelo de datos relacional para integración real de módulos:

- `modules`: inventario de módulos independientes.
- `suites`: soluciones integradas orientadas a misión de negocio.
- `suite_modules`: relación N:M entre suites y módulos.
- `integration_runs`: histórico de simulaciones de integración.

Nuevas capacidades funcionales implementadas:

- creación de suites con responsable y misión,
- asociación dinámica de módulos por suite,
- cálculo de métricas agregadas (coste, valor, complejidad),
- simulación de integración con estimación de ROI,
- almacenamiento histórico de simulaciones para auditoría.

### 2.3 API desarrollada

Endpoints principales:

- `GET /api/overview`
- `GET /api/catalog`
- `POST /api/modules`
- `GET /api/suites`
- `POST /api/suites`
- `GET /api/suites/<id>`
- `POST /api/suites/<id>/modules`
- `POST /api/suites/<id>/simulate`

### 2.4 Mejoras estéticas y visuales

La interfaz se rediseña completamente respecto al listado clásico:

- layout en tres paneles (catálogo, diseñador de suites, simulación),
- diseño cálido y profesional con jerarquía visual clara,
- tarjetas con estado, métricas y filtros por familia,
- experiencia guiada para construir suites y simular impacto.

## 3. Aplicación práctica

Caso práctico implementado: **Suite Comercial 360**.

Integra módulos de marketing, gestión ERP, facturación e inteligencia artificial para pasar de herramientas aisladas a una solución unificada orientada a captación, operación y decisión empresarial.

Proceso de uso:

1. Seleccionar módulos del catálogo.
2. Crear suite con misión de negocio.
3. Guardar la integración módulo-suite.
4. Ejecutar simulación de integración.
5. Analizar ROI estimado y recomendación.

## 4. Conclusión

La actividad cumple el enfoque de segundo curso al incorporar:

- **modificaciones funcionales profundas** (nuevo modelo relacional + simulador + APIs),
- **modificaciones visuales relevantes** (UI completa orientada a operación),
- una misión de mayor calado: convertir un catálogo disperso en un sistema de planificación de suites empresariales.

Como mejora futura, se propone incorporar dependencias técnicas entre módulos y escenarios de simulación por fases de implantación.
