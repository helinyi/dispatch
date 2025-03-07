import logging

from dispatch.case.models import Case
from dispatch.case.type import service as case_type_service
from dispatch.database.core import SessionLocal, resolve_attr
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.incident import service as incident_service
from dispatch.incident.models import Incident
from dispatch.incident.type import service as incident_type_service
from dispatch.plugin import service as plugin_service

from .models import Ticket, TicketCreate
from .service import create


log = logging.getLogger(__name__)


def create_incident_ticket(incident: Incident, db_session: SessionLocal):
    """Creates a ticket for an incident."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Incident ticket not created. No ticket plugin enabled.")
        return

    title = incident.title
    if incident.visibility == Visibility.restricted:
        title = incident.incident_type.name

    incident_type_plugin_metadata = incident_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=incident.project.id,
        incident_type_in=incident.incident_type,
    ).get_meta(plugin.plugin.slug)

    ticket = plugin.instance.create(
        incident.id,
        title,
        # incident.incident_type.name,
        # incident.incident_severity.name,
        # incident.incident_priority.name,
        incident.commander.individual.email,
        incident.reporter.individual.email,
        incident_type_plugin_metadata,
        db_session=db_session,
    )
    ticket.update({"resource_type": plugin.plugin.slug})

    event_service.log(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Incident ticket created",
        incident_id=incident.id,
    )

    return ticket


def update_incident_ticket(
    incident_id: int,
    db_session: SessionLocal,
):
    """Updates an incident ticket."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Ticket not updated. No ticket plugin enabled.")
        return

    title = incident.title
    description = incident.description
    if incident.visibility == Visibility.restricted:
        title = description = incident.incident_type.name

    incident_type_plugin_metadata = incident_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=incident.project.id,
        incident_type_in=incident.incident_type,
    ).get_meta(plugin.plugin.slug)

    total_cost = 0
    if incident.total_cost:
        total_cost = incident.total_cost

    plugin.instance.update(
        incident.ticket.resource_id,
        title,
        description,
        incident.incident_type.name,
        incident.incident_severity.name,
        incident.incident_priority.name,
        incident.status.lower(),
        incident.commander.individual.email,
        incident.reporter.individual.email,
        resolve_attr(incident, "conversation.weblink"),
        resolve_attr(incident, "incident_document.weblink"),
        resolve_attr(incident, "storage.weblink"),
        resolve_attr(incident, "conference.weblink"),
        total_cost,
        incident_type_plugin_metadata=incident_type_plugin_metadata,
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Incident ticket updated",
        incident_id=incident.id,
    )


def create_case_ticket(case: Case, db_session: SessionLocal):
    """Creates a ticket for a case."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Case ticket not created. No ticket plugin enabled.")
        return

    title = case.title
    if case.visibility == Visibility.restricted:
        title = case.case_type.name

    case_type_plugin_metadata = case_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=case.project.id,
        case_type_in=case.case_type,
    ).get_meta(plugin.plugin.slug)

    # we create the external case ticket
    try:
        external_ticket = plugin.instance.create_case_ticket(
            case.id,
            title,
            case.assignee.individual.email,
            case_type_plugin_metadata,
            db_session=db_session,
        )
    except Exception as e:
        log.exception(e)
        return

    if not external_ticket:
        log.error(f"Case ticket not created. Plugin {plugin.plugin.slug} encountered an error.")
        return

    external_ticket.update({"resource_type": plugin.plugin.slug})

    # we create the internal case ticket
    ticket_in = TicketCreate(**external_ticket)
    ticket = create(db_session=db_session, ticket_in=ticket_in)
    case.ticket = ticket
    case.name = external_ticket["resource_id"]

    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Case ticket created",
        case_id=case.id,
    )

    return ticket


def update_case_ticket(
    case: Case,
    db_session: SessionLocal,
):
    """Updates an case ticket."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Ticket not updated. No ticket plugin enabled.")
        return

    title = case.title
    description = case.description
    if case.visibility == Visibility.restricted:
        title = description = case.case_type.name

    case_type_plugin_metadata = case_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=case.project.id,
        case_type_in=case.case_type,
    ).get_meta(plugin.plugin.slug)

    # we update the external case ticket
    try:
        plugin.instance.update_case_ticket(
            case.ticket.resource_id,
            title,
            description,
            case.resolution,
            case.case_type.name,
            case.case_severity.name,
            case.case_priority.name,
            case.status.lower(),
            case.assignee.individual.email,
            resolve_attr(case, "case_document.weblink"),
            resolve_attr(case, "storage.weblink"),
            case_type_plugin_metadata=case_type_plugin_metadata,
        )
    except Exception as e:
        log.exception(e)
        return

    event_service.log_case_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Case ticket updated",
        case_id=case.id,
    )


def delete_ticket(ticket: Ticket, db_session: SessionLocal):
    """Deletes a ticket."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=ticket.case.project.id, plugin_type="ticket"
    )
    if plugin:
        try:
            plugin.instance.delete(ticket_id=ticket.resource_id)
        except Exception as e:
            log.exception(e)
    else:
        log.warning("Ticket not deleted. No ticket plugin enabled.")
