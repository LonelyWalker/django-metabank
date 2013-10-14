from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class AppMenu(Menu):
    def get_nodes(self, request):
        nodes = [
            NavigationNode(_('Dashboard'), reverse('index'), 0, attr={'icon': 'icon-desktop'}),
            NavigationNode(_('Pools'), reverse('pools_list'), 1, attr={'icon': 'eicon-rocket'}),

            NavigationNode(_('Statistic'), '', 3, attr={'icon': 'icon-bar-chart', 'slug': 'statistic'}),
            NavigationNode(_('Device hashrate'), reverse('devicehr'), 0, 3),
            #NavigationNode(_('Realtime'), reverse('realtime'), 1, 3),
            NavigationNode(_('Chip info'), reverse('chip-info'), 2, 3),

            #NavigationNode(_('Settings'), '', 4, attr={'icon': 'icon-cog', 'slug': 'settings'}),
            #NavigationNode(_('Network'), reverse('settings_network'), 0, 4),

            NavigationNode(_('Logs'), reverse('logview'), 5, attr={'icon': 'icon-reorder'})
        ]
        return nodes

menu_pool.register_menu(AppMenu)
