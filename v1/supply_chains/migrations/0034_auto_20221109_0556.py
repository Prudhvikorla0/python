# Generated by Django 4.0.4 on 2022-11-09 05:56

from django.db import migrations


def add_invited_by(apps, schema_editor):
    from django.db.models import Q
    Node = apps.get_model('nodes', 'Node')
    Connection = apps.get_model('supply_chains', 'Connection')
    nodes = Node.objects.all()
    for node in nodes:
        inviter = node.invited_by
        connections = Connection.objects.filter(
            Q(source=node, target=inviter)| Q(
            source=inviter, target=node)).distinct()
        connections.update(invited_by=inviter)


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0033_connection_invited_by'),
    ]

    operations = [
        migrations.RunPython(add_invited_by),
    ]