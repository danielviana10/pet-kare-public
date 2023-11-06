from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from groups.models import Group
from pets.models import Pet

from pets.serializers import PetSerializer
from traits.models import Trait


class PetView(APIView, PageNumberPagination):
    def post(self, req: Request) -> Response:
        serializer = PetSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)

        group_list = serializer.validated_data.pop("group")
        traits_list = serializer.validated_data.pop("traits")

        group_object = Group.objects.filter(
            scientific_name__iexact=group_list["scientific_name"].lower()
        ).first()

        if not group_object:
            group_object = Group.objects.create(**group_list)

        pet_object = Pet.objects.create(
            **serializer.validated_data, group=group_object
        )  # noqa

        for traits_dict in traits_list:
            traits_object = Trait.objects.filter(
                name__iexact=traits_dict["name"].lower()
            ).first()
            if not traits_object:
                traits_object = Trait.objects.create(**traits_dict)

            pet_object.traits.add(traits_object)

        serializer = PetSerializer(pet_object)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        trait = request.query_params.get("trait", None)
        pets = Pet.objects.all()

        if trait:
            pets = pets.filter(traits__name__iexact=trait.lower())

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)
