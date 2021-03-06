from django.test import TestCase, override_settings

from wagtail.tests.utils import WagtailTestUtils

from flags.models import FlagState


class TestWagtailFlagsViews(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

        self.dbonly_flag = FlagState.objects.create(
            name='DBONLY_FLAG',
            condition='boolean',
            value='True',
            required=False
        )

    def test_flags_index(self):
        response = self.client.get('/admin/flags/')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'FLAG_ENABLED')
        self.assertContains(response, 'FLAG_DISABLED')
        self.assertContains(response, 'DBONLY_FLAG')
        self.assertContains(response, '<b>enabled</b> when')
        self.assertContains(response, '<b>enabled</b> for')

    def test_flag_create(self):
        response = self.client.get('/admin/flags/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/flags/create/', {'name': 'NEW_FLAG'}
        )
        self.assertRedirects(response, '/admin/flags/NEW_FLAG/')
        self.assertEqual(FlagState.objects.count(), 2)
        new_flag_condition = FlagState.objects.get(name='NEW_FLAG')
        self.assertEqual(new_flag_condition.condition, 'boolean')
        self.assertEqual(new_flag_condition.value, 'False')
        self.assertEqual(new_flag_condition.required, False)

    @override_settings(
        FLAGS={'WAGTAILFLAGS_ADMIN_BIG_LIST': [('boolean', True)]}
    )
    def test_flag_create_big_list(self):
        response = self.client.post(
            '/admin/flags/create/', {'name': 'NEW_FLAG'}
        )
        self.assertRedirects(response, '/admin/flags/#NEW_FLAG')

    def test_flag_create_existing(self):
        response = self.client.get('/admin/flags/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/flags/create/', {'name': 'DBONLY_FLAG'}
        )
        self.assertContains(response, 'Flag named DBONLY_FLAG already exists')

    def test_flag_index(self):
        response = self.client.get('/admin/flags/FLAG_DISABLED/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FLAG_DISABLED')
        self.assertContains(response, 'path matches')
        self.assertContains(response, 'Enable FLAG_DISABLED')

    def test_flag_index_enabled(self):
        response = self.client.get('/admin/flags/FLAG_ENABLED/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Disable FLAG_ENABLED')

    def test_flag_index_disabled(self):
        response = self.client.get('/admin/flags/FLAG_DISABLED/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enable FLAG_DISABLED')

    def test_flag_index_enabled_required_true(self):
        response = self.client.get('/admin/flags/FLAG_ENABLED/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Disable FLAG_ENABLED')

    def test_flag_index_disabled_required_true(self):
        response = self.client.get('/admin/flags/FLAG_ENABLED/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Disable FLAG_ENABLED')

    def test_enable_flag(self):
        condition_query = FlagState.objects.filter(name='FLAG_DISABLED')
        self.assertEqual(len(condition_query.all()), 0)

        response = self.client.get(
            '/admin/flags/FLAG_DISABLED/', {'enable': ''}
        )
        self.assertRedirects(response, '/admin/flags/FLAG_DISABLED/')
        self.assertEqual(len(condition_query.all()), 1)
        self.assertEqual(condition_query.first().condition, 'boolean')
        self.assertEqual(condition_query.first().value, 'True')

    @override_settings(
        FLAGS={
            'WAGTAILFLAGS_ADMIN_BIG_LIST': [('boolean', True)],
            'FLAG_DISABLED': [],
        }
    )
    def test_enable_flag_big_list(self):
        response = self.client.get(
            '/admin/flags/FLAG_DISABLED/', {'enable': ''}
        )
        self.assertRedirects(response, '/admin/flags/#FLAG_DISABLED')

    def test_enable_flag_with_required_true(self):
        condition_query = FlagState.objects.filter(name='FLAG_DISABLED')
        self.assertEqual(len(condition_query.all()), 0)

        self.client.get('/admin/flags/FLAG_DISABLED/', {'enable': ''})
        self.assertEqual(len(condition_query.all()), 1)
        self.assertEqual(condition_query.first().condition, 'boolean')
        self.assertEqual(condition_query.first().value, 'True')

    def test_disable_flag(self):
        condition_query = FlagState.objects.filter(name='DBONLY_FLAG')
        self.client.get('/admin/flags/DBONLY_FLAG/', {'disable': ''})
        self.assertEqual(len(condition_query.all()), 1)
        self.assertEqual(condition_query.first().condition, 'boolean')
        self.assertEqual(condition_query.first().value, 'False')

    def test_disable_flag_with_required_true(self):
        condition_query = FlagState.objects.filter(name='DBONLY_FLAG')
        self.client.get('/admin/flags/DBONLY_FLAG/', {'disable': ''})
        self.assertEqual(len(condition_query.all()), 1)
        self.assertEqual(condition_query.first().condition, 'boolean')
        self.assertEqual(condition_query.first().value, 'False')

    def test_create_flag_condition(self):
        response = self.client.get('/admin/flags/DBONLY_FLAG/create/')
        self.assertEqual(response.status_code, 200)

        params = {
            'condition': 'path matches',
            'value': '/db_path',
        }
        response = self.client.post('/admin/flags/DBONLY_FLAG/create/', params)
        self.assertRedirects(response, '/admin/flags/DBONLY_FLAG/')
        self.assertEqual(len(FlagState.objects.all()), 2)

    @override_settings(
        FLAGS={'WAGTAILFLAGS_ADMIN_BIG_LIST': [('boolean', True)]}
    )
    def test_create_flag_condition_big_list(self):
        params = {
            'condition': 'path matches',
            'value': '/db_path',
        }
        response = self.client.post('/admin/flags/DBONLY_FLAG/create/', params)
        self.assertRedirects(response, '/admin/flags/#DBONLY_FLAG')

    def test_edit_flag_condition(self):
        condition_obj = FlagState.objects.create(
            name='DBONLY_FLAG',
            condition='user',
            value='liberty'
        )
        response = self.client.get(
            '/admin/flags/DBONLY_FLAG/{}/'.format(condition_obj.pk)
        )
        self.assertEqual(response.status_code, 200)

        params = {
            'condition': 'user',
            'value': 'justice',
        }

        response = self.client.post(
            '/admin/flags/DBONLY_FLAG/{}/'.format(condition_obj.pk),
            params
        )
        self.assertRedirects(response, '/admin/flags/DBONLY_FLAG/')
        self.assertEqual(
            FlagState.objects.get(pk=condition_obj.pk).value,
            'justice'
        )

    @override_settings(
        FLAGS={'WAGTAILFLAGS_ADMIN_BIG_LIST': [('boolean', True)]}
    )
    def test_edit_flag_condition_big_list(self):
        condition_obj = FlagState.objects.create(
            name='DBONLY_FLAG',
            condition='user',
            value='liberty'
        )
        params = {
            'condition': 'user',
            'value': 'justice',
        }
        response = self.client.post(
            '/admin/flags/DBONLY_FLAG/{}/'.format(condition_obj.pk),
            params
        )
        self.assertRedirects(response, '/admin/flags/#DBONLY_FLAG')

    def test_delete_flag_condition(self):
        condition_obj = FlagState.objects.create(
            name='DBONLY_FLAG',
            condition='user',
            value='liberty'
        )
        self.assertEqual(len(FlagState.objects.all()), 2)
        response = self.client.get(
            '/admin/flags/DBONLY_FLAG/{}/delete/'.format(condition_obj.pk)
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/flags/DBONLY_FLAG/{}/delete/'.format(condition_obj.pk)
        )
        self.assertRedirects(response, '/admin/flags/DBONLY_FLAG/')
        self.assertEqual(len(FlagState.objects.all()), 1)

    @override_settings(
        FLAGS={'WAGTAILFLAGS_ADMIN_BIG_LIST': [('boolean', True)]}
    )
    def test_delete_flag_condition_big_list(self):
        condition_obj = FlagState.objects.create(
            name='DBONLY_FLAG',
            condition='user',
            value='liberty'
        )
        self.assertEqual(len(FlagState.objects.all()), 2)
        response = self.client.post(
            '/admin/flags/DBONLY_FLAG/{}/delete/'.format(condition_obj.pk)
        )
        self.assertRedirects(response, '/admin/flags/#DBONLY_FLAG')
