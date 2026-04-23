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
  <kbd>Figura 2</kbd> <br>
  <em>"apertura selectiva del puerto 5000 y habilitación de Health Checks para el correcto funcionamiento del balanceador de carga. Esta configuración garantiza que solo el tráfico legítimo alcance las instancias, manteniendo la integridad de la red interna y optimizando la disponibilidad del servicio mediante el monitoreo constante del estado de las VMs."</em>
</p>


### Backends
Se crearon dos VMs manuales:

- una en `southamerica-west1-a`
- una en `southamerica-west1-b`

<p align="center">
  <img src="Capturas GCP/app.py.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 4</kbd> <br>
  <em>"SScript app.py: Lógica del servidor web python (Flask) configurada para responder por el puerto 5000. Cada instancia se gestiona de forma individual, permitiendo la ejecución del servicio y la muestra de imágenes dinámicas para validar visualmente que el balanceador de carga está distribuyendo el tráfico entre los diferentes nodos"</em>
</p>

Características:
- sin IP pública
- acceso por SSH
- servicio Python simple corriendo en puerto `5000`

Cada backend responde contenido distinto, lo que permite validar visualmente la distribución de tráfico del Load Balancer.

<p align="center">
  <img src="Capturas GCP/VMs.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 5</kbd> <br>
  <em>"Captura del panel de Compute Engine mostrando la implementación multi-zona. Se observa la ausencia de IPs públicas en las instancias para garantizar la seguridad perimetral, permitiendo únicamente el acceso a través del Load Balancer o vía SSH/IAP."</em>
</p>

### Instance Groups
Se utilizaron dos unmanaged instance groups:

- uno por zona
- cada uno contiene una VM
Named port configurado:

- `http-backend:5000`

<p align="center">
  <img src="Capturas GCP/instancegroups.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 6</kbd> <br>
  <em>"Vista detallada de los Unmanaged Instance Groups donde se configuró el mapeo de servicios mediante puertos con nombre (Named Ports). Esta definición es fundamental para que el Backend Service del Load Balancer pueda comunicarse con las aplicaciones que corren en el puerto TCP 5000 dentro de cada máquina virtual."</em>
</p>

### Load Balancer
Se configuró un Application Load Balancer HTTP externo con:

- frontend público en puerto `80`
- backend service basado en instance groups
- health check HTTP al path `/` sobre puerto `5000`

<p align="center">
  <img src="Capturas GCP/loadbalancer.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 7</kbd> <br>
  <em>"Verificación de Health Checks exitosa: Confirmación de disponibilidad de las instancias mediante el puerto TCP:5000, validando la correcta configuración de las reglas de Firewall Ingress."</em>
</p>

## Funcionamiento

El Load Balancer distribuye tráfico entre dos backends privados ubicados en distintas zonas.

Se validó:

- acceso público al balanceador
- llegada del tráfico a instancias sin IP pública
- distribución de tráfico entre backends
- failover al apagar una de las VMs
- health checks exitosos con respuesta HTTP 200

<p align="center">
  <img src="Capturas GCP/loadbalancermonitoring.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 8</kbd> <br>
  <em>"En la fase inicial de pruebas (como se ve en la captura), el gráfico de monitoreo registró tráfico en estado 'Invalid'. Esto ocurrió porque el balanceador recibió peticiones antes de que las instancias completaran el proceso de Health Check. Una vez que el firewall permitió el paso de las sondas de salud y las instancias pasaron a estado 'Healthy', el tráfico comenzó a fluir correctamente hacia los Backends, estabilizando el servicio."</em>
</p>

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

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="Capturas GCP/pipifeliz.png" width="300px"><br>
        <b>Instancia A: Nodo 1</b><br>
        <i>Estado: Pipi Feliz</i>
      </td>
      <td align="center">
        <img src="Capturas GCP/pipienojado.png" width="300px"><br>
        <b>Instancia B: Nodo 2</b><br>
        <i>Estado: Pipi Enojado</i>
      </td>
    </tr>
  </table>
  <p align="center">
    <sub><b>Evidencia técnica:</b> El Load Balancer distribuye las peticiones entre los distintos backends, 
    permitiendo que cada nodo responda con una imagen diferente según la lógica del script <code>app.py</code>.</sub>
  </p>

  <br>

  <p align="center">
    <b>Y para finalizar con la retórica de LinkedIn...</b><br>
    les presento al ser más hermoso del mundo: <b>Pipi (Máximo)</b>, el verdadero motor y la inspiración detrás de cada línea de código y cada configuración en la nube. 👶💙
  </p>
</div>

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

---

<div align="center">
  <p>
    ¿Querés conectar conmigo o saber más sobre mis proyectos en Google Cloud? <br>
    <a href="https://www.linkedin.com/in/ulises-acu%C3%B1a-bianchi-6a36961b4/ target="_blank">
      <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Profile">
    </a>
  </p>
  <sub>Desarrollado con ❤️ Ulises Acuña Bianchi - 2026</sub>
</div>
