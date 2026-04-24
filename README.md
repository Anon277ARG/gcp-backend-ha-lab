# GCP Load Balancer with Private Backends
Backend high availability architecture in GCP with Load Balancer and private VMs

Hands-on Google Cloud Platform project focused on mastering backend infrastructure and high availability concepts.

## Objective

Build a simple yet realistic web architecture featuring:

- Private backends
- Public load balancer
- Health checks
- Multi-zone high availability
- Subsequent migration to Managed Instance Groups (MIG)

## Current Architecture

The current architecture consists of:

- 1 Custom VPC
- 1 Subnet with the range `10.0.0.0/24`
- 2 Private Virtual Machines in different zones
- 2 Unmanaged Instance Groups
- 1 Public HTTP Application Load Balancer
- 1 HTTP Health Check** on port `5000`

## Components

### Network
- Custom VPC manually created
- Subnet setup with the range `10.0.0.0/24`
- Internal connectivity between instances verified

  
<p align="center">
  <img src="Capturas GCP/subred.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 1</kbd> <br>
  <em>"Screenshot of the subnets panel in Google Cloud. The regional segmentation of the default network is observed, highlighting the active subnet in southamerica-west1 (Santiago, Chile). This configuration ensures that the project resources are geographically located to minimize latency for end users in the region."</em>
</p>



### Firewall
Rules configured via network tags.

Primary tag used:

- `backend`

### Relevant rules:
- allow internal HTTP traffic to port 5000
- allow Google Cloud health checks
- allow Load Balancer traffic to the backends

<p align="center">
  <img src="Capturas GCP/firewall.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 2</kbd> <br>
  <em>"Selective opening of port 5000 and enabling of Health Checks for the correct operation of the load balancer. This configuration ensures that only legitimate traffic reaches the instances, maintaining the integrity of the internal network and optimizing service availability through the constant monitoring of the status of the VMs."</em>
</p>


### Backends
Two manual VMs were created:

- one in `southamerica-west1-a`
- one in `southamerica-west1-b`


<p align="center">
  <img src="Capturas GCP/app.py.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 3</kbd> <br>
  <em>"app.py Script: Python web server logic (Flask) configured to respond on port 5000. Each instance is managed individually, allowing the service to run and display dynamic images to visually validate that the load balancer is distributing traffic across thhe different nodes."</em>
</p>

Characteristics:
- no public IP
- SSH access
- simple Python service running on port `5000`
Each backend responds with different content, allowing for visual validation of the Load Balancer's traffic distribution.

<p align="center">
  <img src="Capturas GCP/VMs.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 4</kbd> <br>
  <em>"Screenshot of the Compute Engine panel showing the multi-zone implementation. The absence of public IPs on the instances is observed to ensure perimeter security, allowing access only through the Load Balancer or via SSH/IAP."</em>
</p>



### Instance Groups
Two unmanaged instance groups were used:

- one per zone
- each one contains a VM

Configured named port:
- `http-backend:5000`

<p align="center">
  <img src="Capturas GCP/instancegroups.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 5</kbd> <br>
  <em>"Detailed view of the Unmanaged Instance Groups where service mapping was configured using Named Ports. This definition is essential for the Load Balancer's Backend Service to communicate with the applications running on TCP port 5000 within each virtual machine."</em>
</p>

### Load Balancer
An external HTTP Application Load Balancer was configured with:

- public frontend on port `80`
- backend service based on instance groups
- HTTP health check to path `/` on port `5000`

<p align="center">
  <img src="Capturas GCP/loadbalancer.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 6</kbd> <br>
  <em>"Successful Health Check verification: Confirmation of instance availability through TCP port 5000, validating the correct configuration of the Ingress Firewall rules."</em>
</p>

## Operation

The Load Balancer distributes traffic between two private backends located in different zones.

Validated:

- public access to the balancer
- traffic delivery to instances without public IPs
- traffic distribution between backends
- failover when shutting down one of the VMs
- successful health checks with HTTP 200 response

<p align="center">
  <img src="Capturas GCP/loadbalancermonitoring.png" alt="Panel de VMs en GCP" width="850">
  <br>
  <kbd>Figura 7</kbd> <br>
  <em>"In the initial testing phase (as seen in the screenshot), the monitoring chart registered traffic in an 'Invalid' state. This occurred because the load balancer received requests before the instances completed the Health Check process. Once the firewall allowed the health probes to pass and the instances transitioned to a 'Healthy' state, traffic began to flow correctly to the Backends, stabilizing the service."</em>
</p>

## Performed tests

### Correct validations

- Load Balancer accessible from public IP
- private backends responding correctly
- traffic distributed between instances
- functional failover when turning off a VM
- health checks working correctly

### Problems found and resolved

- syntax error in health check requests
- port 5000 occupied by previous processes
- errors when trying to start the Python service
- confusion between local files, Cloud Shell, and files within the VM
- initial use of apt in startup script blocked by unattended-upgrades



## Visual demo

As visual proof of the balancing, each backend serves different content.
In one of the tests, each VM showed a different image through the Load Balancer, allowing the change of backend to be clearly observed upon refreshing.

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="Capturas GCP/pipifeliz.png" width="300px"><br>
        <b>Instancia A: Nodo 1</b><br>
        <i>Estado: Pipi is happy</i>
      </td>
      <td align="center">
        <img src="Capturas GCP/pipienojado.png" width="300px"><br>
        <b>Instancia B: Nodo 2</b><br>
        <i>Estado: Pipi is mad</i>
      </td>
    </tr>
  </table>
  <p align="center">
    <sub><b>Technical evidence:</b> The Load Balancer distributes the requests among the different backends,
allowing each node to respond with a different image according to the script's logic <code>app.py</code>.</sub>
  </p>

  <br>

  <p align="center">
    <b>And to finish with the LinkedIn rhetoric...</b><br>
    I present to you the most beautiful being in the world: <b>Pipi (Máximo)</b>, the true engine and the inspiration behind every line of code and every cloud configuration. 👶💙
  </p>
</div>

## Next steps

- validate corrected instance template
- migrate to Managed Instance Group
- configure autohealing
- replace unmanaged instance groups
- eliminate manual SSH intervention
- leave the architecture ready to scale

## Technologies used

- Google Cloud Platform
- Compute Engine
- VPC
- Firewall Rules
- Unmanaged Instance Groups
- Application Load Balancer
- Health Checks
- Python `http.server`

## Key learnings

- This project allowed for a practical understanding of:
- difference between zonal, regional, and global resources
- real-world functioning of a Load Balancer
- relationship between backend service, instance groups, and health checks
- importance of validating each layer separately
- real-world debugging issues when working with infrastructure

---

<p align="center">
  Do you want to connect with me or learn more about my projects on Google Cloud? <br>
  <a href="https://www.linkedin.com/in/ulises-acu%C3%B1a-bianchi-6a36961b4/" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Profile">
  </a>
  <br>
  <sub>developed with ❤️ by Ulises Acuña Bianchi - 2026</sub>
</p>
