# GCP Load Balancer with Private Backends
Backend high availability architecture in GCP with Load Balancer and private VMs

Proyecto práctico en Google Cloud Platform orientado a aprender conceptos de infraestructura backend y alta disponibilidad.

## Objetivo

Construir una arquitectura web simple pero realista con:

- backends privados
- load balancer público
- health checks
- alta disponibilidad entre zonas
- migración posterior a Managed Instance Groups (MIG)

## Arquitectura actual

La arquitectura actual está compuesta por:

- 1 VPC custom
- 1 subred con rango `10.0.0.0/24`
- 2 máquinas virtuales privadas en zonas distintas
- 2 unmanaged instance groups
- 1 Application Load Balancer HTTP público
- 1 health check HTTP sobre el puerto `5000`

## Componentes

### Red
- VPC custom creada manualmente
- subred configurada dentro del rango `10.0.0.0/24`
- conectividad interna entre instancias validada

<p align="center">
  <img src="Capturas GCP/subred.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 1</kbd> <br>
  <em>"Captura del panel de subredes en Google Cloud. Se observa la segmentación regional de la red default, destacando la subred activa en southamerica-west1 (Santiago, Chile). Esta configuración asegura que los recursos del proyecto estén localizados geográficamente para minimizar la latencia hacia los usuarios finales en la región."</em>
</p>

### Firewall
Reglas configuradas mediante network tags.

Tag principal utilizado:

- `backend`

Reglas relevantes:
- permitir tráfico HTTP interno al puerto `5000`
- permitir health checks de Google Cloud
- permitir tráfico del Load Balancer hacia los backends

<p align="center">
  <img src="Capturas GCP/firewall.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 1</kbd> <br>
  <em>"apertura selectiva del puerto 5000 y habilitación de Health Checks para el correcto funcionamiento del balanceador de carga. Esta configuración garantiza que solo el tráfico legítimo alcance las instancias, manteniendo la integridad de la red interna y optimizando la disponibilidad del servicio mediante el monitoreo constante del estado de las VMs."</em>
</p>


### Backends
Se crearon dos VMs manuales:

- una en `southamerica-west1-a`
- una en `southamerica-west1-b`

Características:
- sin IP pública
- acceso por SSH
- servicio Python simple corriendo en puerto `5000`

Cada backend responde contenido distinto, lo que permite validar visualmente la distribución de tráfico del Load Balancer.

### Instance Groups
Se utilizaron dos unmanaged instance groups:

- uno por zona
- cada uno contiene una VM

[Panel que muestra VMs con IPs Privadas] (gcp-backend-ha-lab/Capturas GCP/VMs.png)
<p align="center">
  <img src="Capturas GCP/VMs.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 1</kbd> <br>
  <em>"Captura del panel de Compute Engine mostrando la implementación multi-zona. Se observa la ausencia de IPs públicas en las instancias para garantizar la seguridad perimetral, permitiendo únicamente el acceso a través del Load Balancer o vía SSH/IAP."</em>
</p>
Named port configurado:

- `http-backend:5000`

### Load Balancer
Se configuró un Application Load Balancer HTTP externo con:

- frontend público en puerto `80`
- backend service basado en instance groups
- health check HTTP al path `/` sobre puerto `5000`

## Funcionamiento

El Load Balancer distribuye tráfico entre dos backends privados ubicados en distintas zonas.

Se validó:

- acceso público al balanceador
- llegada del tráfico a instancias sin IP pública
- distribución de tráfico entre backends
- failover al apagar una de las VMs
- health checks exitosos con respuesta HTTP 200

## Pruebas realizadas

### Validaciones correctas
- Load Balancer accesible desde IP pública
- backends privados respondiendo correctamente
- tráfico distribuido entre instancias
- failover funcional al apagar una VM
- health checks funcionando correctamente

### Problemas encontrados y resueltos
- error de sintaxis en requests del health check
- puerto `5000` ocupado por procesos previos
- errores al intentar arrancar el servicio Python
- confusión entre archivos locales, Cloud Shell y archivos dentro de la VM
- uso inicial de `apt` en startup script bloqueado por `unattended-upgrades`

## Demo visual

Como prueba visual del balanceo, cada backend sirve contenido diferente.  
En una de las pruebas, cada VM mostró una imagen distinta a través del Load Balancer, permitiendo observar claramente el cambio de backend al refrescar.

## Próximos pasos

- validar instance template corregido
- migrar a Managed Instance Group
- configurar autohealing
- reemplazar unmanaged instance groups
- eliminar intervención manual por SSH
- dejar la arquitectura lista para escalar

## Tecnologías utilizadas

- Google Cloud Platform
- Compute Engine
- VPC
- Firewall Rules
- Unmanaged Instance Groups
- Application Load Balancer
- Health Checks
- Python `http.server`

## Aprendizajes principales

Este proyecto permitió entender en la práctica:

- diferencia entre recursos zonales, regionales y globales
- funcionamiento real de un Load Balancer
- relación entre backend service, instance groups y health checks
- importancia de validar cada capa por separado
- problemas reales de debugging al trabajar con infraestructura
