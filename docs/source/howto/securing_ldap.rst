
Securing LDAP Connections
=========================

When using your project with a production LDAP server, you should always use a secure connection.
The LDAP connections probably will include sensitive information from your domain, like the credentials of the
service account that is begin used by your Django Project, user information of the users on your site and any other custom uses of LDAP in your code.

Securing the connection to your LDAP is somewhat easy, yet still requires some prerequisites and configurations.
Here you will be informed of some practices you can do to better secure your LDAP connections.

.. note::
    | The information provided herein is intended to provide helpful and informative material as it is related to security equipment and services.
    | It is not intended to be taken as legal, accounting, investment, or other professional advice.
    | If you require personal assistance or advice, be sure to consult with a competent professional.
    | We disclaim any responsibility for any liability, loss or risk, personal or otherwise, which is incurred as a consequence, directly or indirectly, of the use and application of any answers provided here or in any of our material.

.. disclaimer source https://securityspecialists.com/disclaimer/

Using SSL/TLS
-------------

SSL/TLS use certificates to establish a secure connection between you and the LDAP service before any data is exchanged.
This practice is called LDAPs, and refers for LDAP over TLS or LDAP over SSL.

To use LDAPs, it needs to be enabled on the LDAP service side.
Each LDAP service has a different setup required to enable LDAPs, you can search docs for your case.

For Active Directory administrators, here is a great guide to enable it for testing: https://techexpert.tips/windows/enabling-the-active-directory-ldap-over-ssl-feature/

Once you have enabled LDAPs on the server, you just need to configure the LDAP Setting ``USE_SSL`` to True.

.. code-block:: python
    :emphasize-lines: 7

    WAUTH_DOMAINS = {
        "EXAMPLE": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="<super secret>",
            USE_SSL=True,
        ),
    }

.. warning::
    This module uses LDAPs by default to provide an easier setup.
    In case your LDAP servers are not capable of LDAPs, you should configure the LDAP setting ``USE_SSL`` to False.

Using NTLM Authentication
-------------------------

NTLM is a protocol used to securely exchange credential information between the client and the server.
It is done by hashing the password with a random generated number provided by the server before sending.

NTLM was originally created by Microsoft to be used in the Windows ecosystem.
It is still in use today, yet it is considered outdated, and has been mainly replaced with Kerberos.

.. seealso::
    `See more detailed explanation about NTLM <https://www.ionos.com/digitalguide/server/know-how/ntlm-nt-lan-manager/#:~:text=NTLM%20is%20a%20collection%20of,servers%20to%20conduct%20mutual%20authentication.>`_

To enable NTLM authentication, you can specify connection's ``authentication`` options in the ``CONNECTION_OPTIONS`` LDAP setting.

.. code-block:: python
    :emphasize-lines: 8-10

    WAUTH_DOMAINS = {
        "EXAMPLE": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="<super secret>",
            USE_SSL=True,
            CONNECTION_OPTIONS={
                "authentication": ldap3.NTLM,
            },
        ),
    }

.. seealso::
    NTLM authentication on ldap3 docs https://ldap3.readthedocs.io/en/latest/bind.html#ntlm

Using Kerberos (SASL)
---------------------

Kerberos is an authentication and authorization protocol designed by MIT in the late '80s.
Today, kerberos is the gold standard authentication and authorization protocol used throughout Windows and other OSs.
It uses tickets to represent the authenticated user and to authorize it to access desired services.

.. seealso::
    Learn more about Kerberos at https://www.simplilearn.com/what-is-kerberos-article

When using kerberos authentication, the credentials given to the LDAP server is the account's kerberos token accessed from the MIT Token Manager.
Therefore, the account running your Django Project will be used when accessing LDAP servers, and no username or password needs to be provided.

In order to use the ldap3 ``SASL`` authentication with the ``KERBEROS`` mechanism, you will need to install the ``gssapi`` package.
To install it you first need to install the MIT Kerberos on the server.

Go to https://web.mit.edu/KERBEROS/dist/ and download the latest MIT Kerberos for Windows as 64-bit MSI Installer, and install it on the server.
Restart will be required after installation is done.

After the restart, edit the ``C:\ProgramData\MIT\Kerberos5\krb5.ini`` and provide the ``default_realm`` setting.
For example:

.. code-block:: ini

    [libdefaults]
        default_realm = EXAMPLE.LOCAL

.. seealso::
    More about the ``krb5.ini`` config file https://web.mit.edu/kerberos/www/krb5-latest/doc/admin/conf_files/krb5_conf.html

Then, install the ``gssapi`` package in your virtualenv::

$ pip install gssapi

Then configure your LDAP connections to use the ``SASL`` authentication with ``KERBEROS`` mechanism like so:

.. code-block:: python
    :emphasize-lines: 8-11

    WAUTH_DOMAINS = {
        "EXAMPLE": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="",
            PASSWORD="",
            USE_SSL=True,
            CONNECTION_OPTIONS={
                "authentication": ldap3.SASL,
                "sasl_mechanism": ldap3.KERBEROS,
            }
        ),
    }

Now you need to get the ticket for that account configured though MIT Token Manager.



.. note::
    Notice the username and password kept as empty strings as they are not necessary in this setup.

Optimize your code
------------------

Securing the LDAP connection in at the protocol level is good, but do not let it deceive you.
It is very important to restrict any unintended operation on the LDAP server, especially write operations.

**Minimize the permissions and delegations of the bind account to the bare minimum possible.**
You can never know how and what could be done through vulnerabilities in your code.

**Never ever write user password or other credentials explicitly inside your code.**
Use instead another way to store your secrets in a protected place. See the tutorial about :doc:`manage_secrets`

**Use ``Reader`` and ``Writer`` cursors from ldap3's abstraction module.**
Using them can help you to avoid unwanted behaviors by simplifying the interface.

**Restrict access to views performing LDAP operations.**
Allow only authenticated users, and implement permission check to avoid compromising your views.

**Use read-only connection when possible.**
By default, LDAP connections are made read-only.
It restricts the execution of write operations at the client level.

In case you need to perform write operations, you will need to explicitly disable read-only.
When doing so, consider **creating a dedicated connection** for writing, with a **different bind account** with the minimal permissions.
This can be done by adding another domain to ``WAUTH_DOMAINS`` setting for the same domain, but with different account and read-only disabled.

.. TODO read and write cursors