# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Log'
        db.delete_table(u'status_log')


    def backwards(self, orm):
        # Adding model 'Log'
        db.create_table(u'status_log', (
            ('temperature', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mhs', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=16, decimal_places=2, blank=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'status', ['Log'])


    models = {
        u'status.logaverage': {
            'Meta': {'object_name': 'LogAverage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mhs': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '16', 'decimal_places': '2', 'blank': 'True'}),
            'temperature': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['status']