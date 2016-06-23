from django.apps import AppConfig


class OfficerAllocationConfig(AppConfig):
    name = 'officer_allocation'
    verbose_name = 'Officer Allocation'

    def ready(self):
        from hooks.templatehook import hook
        from officer_allocation.template_hooks import navbar

        hook.register("navbar", navbar)
        hook.register("landing_page_navbar", navbar)
