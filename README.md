<div align="center">
    <a href="https://cpmerp.com">
        <img src="https://raw.githubusercontent.com/frappe/cpmerp/develop/cpmerp/public/images/cpmerp-logo.png" height="128">
    </a>
    <h2>CPMERP</h2>
    <p align="center">
        <p>ERP made simple</p>
    </p>

[![CI](https://github.com/frappe/cpmerp/actions/workflows/server-tests-mariadb.yml/badge.svg?event=schedule)](https://github.com/frappe/cpmerp/actions/workflows/server-tests-mariadb.yml)
[![Open Source Helpers](https://www.codetriage.com/frappe/cpmerp/badges/users.svg)](https://www.codetriage.com/frappe/cpmerp)
[![codecov](https://codecov.io/gh/frappe/cpmerp/branch/develop/graph/badge.svg?token=0TwvyUg3I5)](https://codecov.io/gh/frappe/cpmerp)
[![docker pulls](https://img.shields.io/docker/pulls/frappe/cpmerp-worker.svg)](https://hub.docker.com/r/frappe/cpmerp-worker)

[https://cpmerp.com](https://cpmerp.com)

</div>

CPMERP as a monolith includes the following areas for managing businesses:

1. [Accounting](https://cpmerp.com/open-source-accounting)
1. [Warehouse Management](https://cpmerp.com/distribution/warehouse-management-system)
1. [CRM](https://cpmerp.com/open-source-crm)
1. [Sales](https://cpmerp.com/open-source-sales-purchase)
1. [Purchase](https://cpmerp.com/open-source-sales-purchase)
1. [HRMS](https://cpmerp.com/open-source-hrms)
1. [Project Management](https://cpmerp.com/open-source-projects)
1. [Support](https://cpmerp.com/open-source-help-desk-software)
1. [Asset Management](https://cpmerp.com/open-source-asset-management-software)
1. [Quality Management](https://cpmerp.com/docs/user/manual/en/quality-management)
1. [Manufacturing](https://cpmerp.com/open-source-manufacturing-erp-software)
1. [Website Management](https://cpmerp.com/open-source-website-builder-software)
1. [Customize CPMERP](https://cpmerp.com/docs/user/manual/en/customize-cpmerp)
1. [And More](https://cpmerp.com/docs/user/manual/en/)

CPMERP is built on the [Frappe Framework](https://github.com/frappe/frappe), a full-stack web app framework built with Python & JavaScript.

## Installation

<div align="center" style="max-height: 40px;">
    <a href="https://frappecloud.com/cpmerp/signup">
        <img src=".github/try-on-f-cloud-button.svg" height="40">
    </a>
    <a href="https://labs.play-with-docker.com/?stack=https://raw.githubusercontent.com/frappe/frappe_docker/main/pwd.yml">
      <img src="https://raw.githubusercontent.com/play-with-docker/stacks/master/assets/images/button.png" alt="Try in PWD" height="37"/>
    </a>
</div>

> Login for the PWD site: (username: Administrator, password: admin)

### Containerized Installation

Use docker to deploy CPMERP in production or for development of [Frappe](https://github.com/frappe/frappe) apps. See https://github.com/frappe/frappe_docker for more details.

### Manual Install

The Easy Way: our install script for bench will install all dependencies (e.g. MariaDB). See https://github.com/frappe/bench for more details.

New passwords will be created for the CPMERP "Administrator" user, the MariaDB root user, and the frappe user (the script displays the passwords and saves them to ~/frappe_passwords.txt).


## Learning and community

1. [Frappe School](https://frappe.school) - Learn Frappe Framework and CPMERP from the various courses by the maintainers or from the community.
2. [Official documentation](https://docs.cpmerp.com/) - Extensive documentation for CPMERP.
3. [Discussion Forum](https://discuss.cpmerp.com/) - Engage with community of CPMERP users and service providers.
4. [Telegram Group](https://cpmerp_public.t.me) - Get instant help from huge community of users.


## Contributing

1. [Issue Guidelines](https://github.com/frappe/cpmerp/wiki/Issue-Guidelines)
1. [Report Security Vulnerabilities](https://cpmerp.com/security)
1. [Pull Request Requirements](https://github.com/frappe/cpmerp/wiki/Contribution-Guidelines)

## License

GNU/General Public License (see [license.txt](license.txt))

The CPMERP code is licensed as GNU General Public License (v3) and the Documentation is licensed as Creative Commons (CC-BY-SA-3.0) and the copyright is owned by Frappe Technologies Pvt Ltd (Frappe) and Contributors.

By contributing to CPMERP, you agree that your contributions will be licensed under its GNU General Public License (v3).

## Logo and Trademark Policy

Please read our [Logo and Trademark Policy](TRADEMARK_POLICY.md).
