from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'follow_amount')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    def follow_amount(self, obj):
        return obj.following.count()


admin.site.register(User, UserAdmin)
