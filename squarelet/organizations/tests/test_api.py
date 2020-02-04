# Standard Library
import json
import time
from unittest.mock import Mock

# Third Party
import pytest
from rest_framework import status
from rest_framework.test import APIClient

# Squarelet
from squarelet.organizations.choices import ChangeLogReason
from squarelet.organizations.models import Charge, Organization
from squarelet.organizations.tests.factories import (
    EntitlementFactory,
    MembershipFactory,
    OrganizationFactory,
    PlanFactory,
)
from squarelet.users.tests.factories import UserFactory


@pytest.mark.django_db()
class TestOrganizationAPI:
    def test_retrieve(self, user_factory, mocker):
        user = user_factory(is_staff=True)
        client = APIClient()
        client.force_authenticate(user=user)
        mocker.patch(
            "squarelet.organizations.models.Customer.stripe_customer",
            default_source=None,
        )
        response = client.get(
            f"/api/organizations/{user.individual_organization.uuid}/"
        )
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert response_json["uuid"] == str(user.individual_organization.uuid)
        assert response_json["name"] == user.individual_organization.name
        assert response_json["individual"]

    def test_create_charge(self, user_factory, mocker):
        mocked = mocker.patch(
            "stripe.Charge.create",
            return_value=Mock(id="charge_id", created=time.time()),
        )
        mocker.patch(
            "squarelet.organizations.models.Customer.stripe_customer",
            default_source="default_source",
        )
        user = user_factory(is_staff=True)
        data = {
            "organization": str(user.individual_organization.uuid),
            "amount": 2700,
            "fee_amount": 5,
            "description": "This is only a test",
            "token": None,
            "save_card": False,
        }
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(f"/api/charges/", data)
        assert response.status_code == status.HTTP_201_CREATED
        response_json = json.loads(response.content)
        assert "card" in response_json
        for field in ("organization", "amount", "fee_amount", "description"):
            assert response_json[field] == data[field]
        mocked.assert_called_once()
        assert Charge.objects.filter(charge_id="charge_id").exists()


@pytest.mark.django_db()
class TestPPOrganizationAPI:
    def test_list(self, api_client):
        """List organizations"""
        size = 10
        OrganizationFactory.create_batch(size)
        response = api_client.get(f"/pp-api/organizations/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_create(self, api_client, user):
        """Create an organization"""
        api_client.force_authenticate(user=user)
        data = {"name": "Test"}
        response = api_client.post(f"/pp-api/organizations/", data)
        assert response.status_code == status.HTTP_201_CREATED
        response_json = json.loads(response.content)
        organization = Organization.objects.get(uuid=response_json["uuid"])
        assert organization.has_admin(user)
        assert organization.receipt_emails.filter(email=user.email).exists()
        assert organization.change_logs.filter(reason=ChangeLogReason.created).exists()

    def test_retrieve(self, api_client, organization):
        """Test retrieving an organization"""
        response = api_client.get(f"/pp-api/organizations/{organization.uuid}/")
        assert response.status_code == status.HTTP_200_OK

    def test_update(self, api_client, user):
        """Test updating an organization"""
        organization = OrganizationFactory(admins=[user])
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            f"/pp-api/organizations/{organization.uuid}/", {"max_users": 42}
        )
        assert response.status_code == status.HTTP_200_OK
        organization.refresh_from_db()
        assert organization.max_users == 42


@pytest.mark.django_db()
class TestPPMembershipAPI:
    def test_list(self, api_client, user):
        """List organizations"""
        size = 10
        organization = OrganizationFactory(admins=[user])
        MembershipFactory.create_batch(size, organization=organization)
        response = api_client.get(
            f"/pp-api/organizations/{organization.uuid}/memberships/"
        )
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size + 1

    def test_retrieve(self, api_client, user):
        """Test retrieving a membership"""
        organization = OrganizationFactory(users=[user])
        response = api_client.get(
            f"/pp-api/organizations/{organization.uuid}/memberships/"
            f"{user.individual_organization_id}/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update(self, api_client, user):
        """Test updating a membership"""
        member = UserFactory()
        organization = OrganizationFactory(admins=[user], users=[member])
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            f"/pp-api/organizations/{organization.uuid}/memberships/"
            f"{member.individual_organization_id}/",
            {"admin": True},
        )
        assert response.status_code == status.HTTP_200_OK
        assert organization.has_admin(member)

    def test_destroy(self, api_client, user):
        member = UserFactory()
        organization = OrganizationFactory(admins=[user], users=[member])
        api_client.force_authenticate(user=user)
        response = api_client.delete(
            f"/pp-api/organizations/{organization.uuid}/memberships/"
            f"{member.individual_organization_id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not organization.has_member(member)


@pytest.mark.django_db()
class TestPPInvitationAPI:
    pass


@pytest.mark.django_db()
class TestPPPlanAPI:
    def test_list(self, api_client):
        """List plans"""
        size = 10
        PlanFactory.create_batch(size)
        response = api_client.get(f"/pp-api/plans/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_retrieve(self, api_client, mocker):
        """Test retrieving a plan"""
        mocker.patch("stripe.Plan.create")
        plan = PlanFactory()
        response = api_client.get(f"/pp-api/plans/{plan.id}/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db()
class TestPPEntitlementAPI:
    def test_list(self, api_client):
        """List entitlements"""
        size = 10
        EntitlementFactory.create_batch(size)
        response = api_client.get(f"/pp-api/entitlements/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_retrieve(self, api_client, entitlement):
        """Test retrieving an entitlement"""
        response = api_client.get(f"/pp-api/entitlements/{entitlement.id}/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db()
class TestPPSubscriptionAPI:
    pass
