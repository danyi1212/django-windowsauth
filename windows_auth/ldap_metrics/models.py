from django.db import models


class LDAPUsage(models.Model):
    timestamp = models.DateTimeField(auto_now=True, db_index=True, help_text="Metrics Collection Time")
    pid = models.IntegerField(help_text="Process ID")
    domain = models.CharField(max_length=128, db_index=True, help_text="Connection's domain")

    initial_connection_start_time = models.DateTimeField(null=True, help_text="Initialization timestamp")
    open_socket_start_time = models.DateTimeField(null=True, help_text="Socket Open timestamp")
    connection_stop_time = models.DateTimeField(null=True, help_text="Close timestamp")
    last_transmitted_time = models.DateTimeField(null=True, help_text="Last message transmitted timestamp")
    last_received_time = models.DateTimeField(null=True, help_text="Last message received timestamp")

    servers_from_pool = models.PositiveSmallIntegerField(default=0, help_text="Num. servers from pool")
    open_sockets = models.PositiveSmallIntegerField(default=0, help_text="Num. of sockets opened")
    closed_sockets = models.PositiveSmallIntegerField(default=0, help_text="Num. of sockets closed")
    wrapped_sockets = models.PositiveSmallIntegerField(default=0, help_text="Num. of sockets wrapped by TLS")

    bytes_transmitted = models.PositiveIntegerField(default=0, help_text="Bytes transmitted")
    bytes_received = models.PositiveIntegerField(default=0, help_text="Bytes received")
    messages_transmitted = models.PositiveIntegerField(default=0, help_text="Messages transmitted")
    messages_received = models.PositiveIntegerField(default=0, help_text="Messages received")

    operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Operations")
    abandon_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Abandon Operations")
    bind_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Bind Operations")
    add_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Add Operations")
    compare_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Compare Operations")
    delete_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Delete Operations")
    extended_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Extended Operations")
    modify_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Modify Operations")
    modify_dn_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Move Operations")
    search_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Search Operations")
    unbind_operations = models.PositiveSmallIntegerField(default=0, help_text="Num. Unbind Operations")

    referrals_received = models.PositiveSmallIntegerField(default=0, help_text="Num. Referrals Received")
    referrals_followed = models.PositiveSmallIntegerField(default=0, help_text="Num. Referrals Followed")
    referrals_connections = models.PositiveSmallIntegerField(default=0, help_text="Num. Referrals Connections")

    restartable_failures = models.PositiveSmallIntegerField(default=0, help_text="Num. Restartable Failures")
    restartable_successes = models.PositiveSmallIntegerField(default=0, help_text="Num. Restartable Successes")

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"
