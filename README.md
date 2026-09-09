# Contapp

Mini ERP contable colombiano con integración a la API de facturación electrónica [Factus](https://www.factus.com.co). Desarrollado como proyecto de portafolio con stack moderno, autenticación real vía Supabase Auth, base de datos PostgreSQL en Supabase, y contenedores Docker para portabilidad.

---

## Tabla de contenidos

1. [Características](#características)
2. [Stack tecnológico](#stack-tecnológico)
3. [Arquitectura](#arquitectura)
4. [Requisitos](#requisitos)
5. [Configuración paso a paso](#configuración-paso-a-paso)
6. [Cómo ejecutar localmente](#cómo-ejecutar-localmente)
7. [Cómo ejecutar con Docker](#cómo-ejecutar-con-docker)
8. [Estructura del proyecto](#estructura-del-proyecto)
9. [Endpoints de la API](#endpoints-de-la-api)
10. [Flujo de autenticación](#flujo-de-autenticación)
11. [Integración con Factus](#integración-con-factus)
12. [Pruebas](#pruebas)
13. [Roadmap y mejoras futuras](#roadmap-y-mejoras-futuras)
14. [Licencia](#licencia)

---

## Características

- Autenticación de usuarios con Supabase Auth (registro/login por email y password).
- Gestión de clientes con datos exigidos por la DIAN.
- Gestión de productos/servicios con impuestos configurables.
- Creación de facturas de venta con ítems, descuentos e impuestos.
- Emisión de facturas electrónicas vía mock de Factus (listo para reemplazar por API real).
- Almacenamiento de respuestas de Factus: número de factura, CUFE, URL de PDF y XML.
- Reportes básicos: ventas totales, impuestos (IVA) y cuentas por cobrar.
- Frontend bilingüe español/inglés con selector de idioma.
- Backend documentado con OpenAPI en `/docs`.
- Infraestructura portable con Docker Compose.

---

## Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Backend | Python 3.14 + FastAPI |
| ORM | SQLModel |
| Base de datos | Supabase PostgreSQL |
| Autenticación | Supabase Auth |
| Frontend | Vue 3 + Vite + Composition API |
| Estilos | TailwindCSS v4 |
| Internacionalización | Vue I18n |
| Contenedores | Docker + Docker Compose |
| Testing | pytest (backend) + Vitest (frontend) |

---

## Arquitectura

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Navegador     │──────▶│  Frontend (Vue)  │──────▶│ Backend (FastAPI│
│                 │◀──────│   Puerto 5173    │◀──────│   Puerto 8000   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                              │                            │
                              ▼                            ▼
                       Supabase Auth              Supabase PostgreSQL
                       (login/register)              (datos de negocio)
```

El frontend se autentica directamente con Supabase Auth usando el `anon key`, obtiene un JWT y lo envía al backend en cada petición. El backend valida el JWT y sincroniza el perfil del usuario en la base de datos PostgreSQL de Supabase.

---

## Requisitos

Para desarrollo local:

- Python 3.14+
- pip
- Node.js 20+
- npm

Para Docker:

- Docker Engine 24+
- Docker Compose 2.20+

Servicios externos:

- Cuenta en [Supabase](https://supabase.com) con proyecto creado.
- (Opcional) Credenciales de sandbox de Factus para pruebas reales.

---

## Configuración paso a paso

### 1. Crear proyecto en Supabase

1. Entra a [https://supabase.com](https://supabase.com) e inicia sesión.
2. Crea una nueva organización si es necesario.
3. Crea un proyecto llamado `contapp` y anota la contraseña de base de datos.
4. Ve a **Project Settings > API** y copia:
   - `Project URL`
   - `anon public` key (JWT, NO el publishable key)
   - `service_role secret` key
5. Ve al botón **Connect > Shared Pooler > Session mode** y copia la connection string de PostgreSQL (IPv4).
6. Después de correr la primera migración, las políticas RLS se crean automáticamente en la base de datos.

### 2. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
DATABASE_URL=postgresql://postgres.tu-proyecto:PASSWORD@aws-region.pooler.supabase.com:5432/postgres
```

> ⚠️ **Nunca subas el archivo `.env` a GitHub.** Ya está incluido en `.gitignore`.

### 3. Configurar variables del frontend

```bash
cp frontend/.env.example frontend/.env
```

Edita `frontend/.env`:

```env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu-anon-key
```

---

## Cómo ejecutar localmente

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear/actualizar tablas
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

La documentación interactiva de FastAPI estará disponible en:

```
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre en el navegador:

```
http://localhost:5173
```

---

## Cómo ejecutar con Docker

Desde la raíz del proyecto:

```bash
docker compose build
docker compose up -d
```

Servicios disponibles:

- Frontend: [http://localhost](http://localhost)
- Backend: [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Para detener:

```bash
docker compose down
```

---

## Estructura del proyecto

```
contapp/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # Endpoints REST
│   │   ├── core/             # Configuración, BD, seguridad
│   │   ├── models/           # Modelos SQLModel
│   │   ├── schemas/          # DTOs Pydantic
│   │   ├── services/         # Lógica de negocio (Factus mock)
│   │   └── main.py           # Punto de entrada FastAPI
│   ├── alembic/              # Migraciones
│   ├── tests/                # Tests pytest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes Vue
│   │   ├── i18n/             # Traducciones ES/EN
│   │   ├── router/           # Vue Router
│   │   ├── services/         # Cliente Axios
│   │   ├── stores/           # Pinia stores
│   │   └── views/            # Vistas de pantallas
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Endpoints de la API

### Autenticación

| Método | Endpoint | Descripción |
| --- | --- | --- |
| POST | `/api/auth/profile` | Crea/actualiza perfil en base de datos |
| GET | `/api/auth/me` | Devuelve perfil del usuario autenticado |

> El registro y login se hacen directamente desde el frontend con Supabase Auth.

### Negocio

| Método | Endpoint | Descripción |
| --- | --- | --- |
| POST | `/api/clients/` | Crear cliente |
| GET | `/api/clients/` | Listar clientes |
| GET | `/api/clients/{id}` | Obtener cliente |
| PUT | `/api/clients/{id}` | Actualizar cliente |
| DELETE | `/api/clients/{id}` | Eliminar cliente |
| POST | `/api/products/` | Crear producto |
| GET | `/api/products/` | Listar productos |
| GET | `/api/products/{id}` | Obtener producto |
| PUT | `/api/products/{id}` | Actualizar producto |
| DELETE | `/api/products/{id}` | Eliminar producto |
| POST | `/api/invoices/` | Crear factura borrador |
| GET | `/api/invoices/` | Listar facturas |
| GET | `/api/invoices/{id}` | Obtener factura |
| POST | `/api/invoices/{id}/emit` | Emitir factura vía Factus |

### Reportes

| Método | Endpoint | Descripción |
| --- | --- | --- |
| GET | `/api/reports/sales-summary` | Resumen de ventas |
| GET | `/api/reports/taxes` | Impuestos IVA de facturas validadas |
| GET | `/api/reports/accounts-receivable` | Cuentas por cobrar |
| GET | `/api/reports/monthly-sales?status=validated\|pending\|rejected\|draft\|all` | Ventas e impuestos agrupados por mes |
| GET | `/api/reports/sales-by-status` | Conteo de facturas por estado |

---

## Flujo de autenticación

1. El usuario ingresa email y password en el frontend.
2. El frontend llama a `supabase.auth.signInWithPassword()`.
3. Supabase Auth devuelve un JWT válido.
4. El frontend almacena el token y lo envía en el header `Authorization: Bearer <token>`.
5. El backend valida el JWT y crea/lee el perfil del usuario en PostgreSQL.
6. Todas las rutas protegidas usan la dependencia `get_current_user`.
7. Todas las tablas de negocio (`users`, `clients`, `products`, `invoices`, `invoice_items`) tienen **RLS activado** con políticas que permiten a cada usuario solo acceder a sus propios datos cuando se usa la API REST de Supabase.

---

## Integración con Factus

Actualmente el servicio de Factus está en modo **mock**. Simula:

- Autenticación y obtención de token.
- Validación de factura ante la DIAN.
- Respuesta con número de factura, CUFE, QR, PDF y XML.

Para usar la API real de Factus:

1. Solicita credenciales de sandbox en [https://www.factus.com.co](https://www.factus.com.co).
2. Actualiza `.env`:

```env
FACTUS_BASE_URL=https://api-sandbox.factus.com.co
FACTUS_USERNAME=tu-usuario-factus
FACTUS_PASSWORD=tu-password-factus
FACTUS_CLIENT_ID=tu-client-id
FACTUS_CLIENT_SECRET=tu-client-secret
```

3. El backend usará `httpx` para conectarse a los endpoints reales de Factus.

### Flujo de emisión real

```
Contapp Backend
   │
   ├──▶ POST /oauth/token (autenticación OAuth2 password)
   │
   └──▶ POST /v2/bills/validate (envía factura a Factus/DIAN)
            │
            ▼
        Respuesta con número, CUFE, QR y URL pública del PDF
            │
            ▼
   Almacenar en PostgreSQL (estado, CUFE, PDF, XML, respuesta cruda)
```

### Estados de factura tras emisión

| Estado | Significado |
| --- | --- |
| `validated` | Factura validada exitosamente ante la DIAN (`is_validated: true`). |
| `pending` | Factura registrada en Factus, aún en proceso de validación DIAN. |
| `rejected` | Factura rechazada por errores de validación. Requiere corrección. |
| `draft` | Factura creada en Contapp pero no enviada a Factus. |

### Envío de correos

El envío de correos al adquiriente es gestionado por el propio Contapp, no por Factus. Por eso en cada emisión se envía `send_email: false`, y las URLs públicas del PDF se usan para notificaciones propias.

---

## Pruebas

### Backend

```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend

```bash
cd frontend
npm run test
```

---

## Roadmap y mejoras futuras

- [x] Conectar emisión de facturas con la API real de Factus.
- [x] Obtener URLs públicas de PDF desde Factus.
- [ ] Recepción de facturas de compra.
- [ ] Notas crédito y débito.
- [x] Dashboard con gráficos de ventas (ApexCharts).
- [ ] Soporte multi-tenant (varias empresas por usuario).
- [x] Tests de integración con TestClient de FastAPI.
- [ ] CI/CD con GitHub Actions.

---

## Licencia

MIT © 2026 Contapp
