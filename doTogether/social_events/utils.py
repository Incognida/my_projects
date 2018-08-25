from django.contrib.auth import get_user_model

from social_events.models import Subcategory, Category


class UpdateValidator:
    def __init__(self, instance, validated_data):
        self.instance = instance
        self.validated_data = validated_data
        self.category_id = self.validated_data.get("category_id", None)
        self.subcategories_ids = self.validated_data.get(
            "subcategories_ids", None
        )

    def validate(self):
        self.validate_members()
        self.validate_date()
        if self.category_id and not self.subcategories_ids:
            self.validate_cat_no_subs()
        elif not self.category_id and self.subcategories_ids:
            self.validate_no_cat_subs()
        elif self.category_id and self.subcategories_ids:
            self.validate_cat_subs()
        self.instance.save()
        return self.instance

    def validate_members(self):
        User = get_user_model()
        max_members = self.validated_data.get('max_members', 0)
        members = self.validated_data.get("members_ids", [])
        black_members = self.validated_data.get('black_members_ids', [])

        if members and black_members and set(black_members) & set(members):
            raise Exception(
                "You can't add members simultaneously to both lists")

        possible_max_members = self.instance.members.count() + len(members)
        if max_members and possible_max_members > max_members:
            raise Exception("Members count is less than 'max_members'")
        elif not max_members and possible_max_members > self.instance.max_members:
            raise Exception("Too much members, try to decrease 'max_members'")

        member_objs = User.objects.filter(pk__in=members)
        black_member_objs = User.objects.filter(pk__in=black_members)
        temp_error = "You have provided not existent users"
        if member_objs.count() != len(members):
            raise Exception(temp_error)
        if black_member_objs.count() != len(black_members):
            raise Exception(temp_error)

        for member in members:
            if member in self.instance.black_list.all():
                self.instance.black_list.remove(member)
            self.instance.members.add(member)
        for black_member in black_members:
            if black_member in self.instance.members.all():
                self.instance.members.remove(black_member)
            self.instance.black_list.add(black_member)

    def validate_date(self):
        ends_at = self.validated_data.get("ends_at", None)
        if ends_at and ends_at < self.instance.starts_at:
            raise Exception(
                "Event can't be finished earlier than it's started"
            )
        self.instance.ends_at = ends_at

    def validate_cat_no_subs(self):
        if self.category_id != self.instance.category_id:
            self.instance.subcategories.clear()
            self.instance.category_id = self.category_id

    def validate_no_cat_subs(self):
        new_subs = self.subs_in_category()
        for sub in new_subs:
            self.instance.subcategories.add(sub)

    def validate_cat_subs(self):
        category = Category.objects.filter(pk=self.category_id).first()
        if not category:
            raise Exception("There is no such category")
        new_subs = self.subs_in_category(category=category)
        if category.pk == self.instance.category_id:
            for sub in new_subs:
                self.instance.subcategories.add(sub)
        else:
            self.instance.subcategories.clear()
            self.instance.category_id = self.category_id
            self.instance.subcategories.set(new_subs)

    def subs_in_category(self, category=None):
        cat_pk = category.pk if category else self.instance.category_id
        new_subs = Subcategory.objects.filter(pk__in=self.subcategories_ids)
        distinct_sub = new_subs.distinct('category_id')
        if not distinct_sub or distinct_sub.count() > 1:
            raise Exception("Subs not in db OR subs "
                            "are not distinct by category")
        if distinct_sub[0].category_id != cat_pk:
            raise Exception("Subs do not belong to category")
        return new_subs
