
Using LDAP in your code
=======================

In addition to just windows authentication and IIS integration, this module provide you with an easy to use LDAP connection interface.

Throughout your code, you can use the ``get_ldap_manager`` function to receive an ``LDAPManager`` manager object fora specified domain.
For example:

.. code-block:: python

    from windows_auth.ldap import get_ldap_manager

    manager = get_ldap_manager("EXAMPLE")
    manager.connection

With the manager, you can access the ldap3 ``Connection`` object, perform LDAP operations like search, add, modify, etc.

Also, you can use the **ldap3 Abstraction Layer** for a simple python interface.
This is how you can use it to query all Active Directory Computer objects:

.. code-block:: python

    reader = manager.get_reader("computer")
    reader.search("name")

And even write to LDAP, like this:

.. code-block:: python

    from ldap3 import Writer

    writer = Writer.from_cursor(reader)
    computer = writer.match("name", "test_computer")[0]
    computer.description = "Hello world!"
    writer.commit()


.. note::
    For Security reasons, the LDAP connections are **read-only** by default.
    In order to write to LDAP, you will need to configure ``READ_ONLY=False`` in the LDAP Settings of each desired domain.

Advice for Model - LDAP relations
---------------------------------

Sometimes it is useful to relate a **Django Model object** to an **LDAP object**.
When doing so, you can easily implement **synchronization**, and enable easy access for **LDAP operation** on that object.
If you plan to do such thing, here are some tips for you:

Store the **LDAP Domain** in which the object is from, either as a **class-level const**, or a **Model Field**.
You may want to event implement a ``get_ldap_manager`` method get the manager for the respective domain.

.. code-block:: python

    class Computer(models.Model):
        # as a const
        DOMAIN = "EXAMPLE"

        # as a field
        domain: str = models.CharField(max_length=128)

        # using a method
        def get_ldap_manager(self) -> LDAPManager:
            return get_ldap_manager(self.domain)

Then implement a method to receive the exact entry for the related LDAP object.

.. code-block:: python

    class Computer(models.Model):
        # ...
        name: str = models.CharField(max_length=128)

        def get_ldap_computer(self, attributes: Optional[Iterable[str]] = None) -> Entry:
            manager = self.get_ldap_manager()
            reader = manager.get_reader("computer", f"name: {self.name}", attributes)
            return reader.search()[0]
