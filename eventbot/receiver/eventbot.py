'''
eventbot receiver implementation.

General flow:

1. User messages bot: ``@eventbot create``
1. eventbot receives a message via ``create_event_command` function and responds with an interactive message,
   letting the user click a create button to create a new event
1. User clicks create button
1. eventbot receives interactive message via ``interactive_event_handler`` function and responds back with a dialog
1. User fills in dialog, and submits the dialog
1. eventbot receives interactive message via ``handle_interactive_event_for_events`` function and responds back, with
   an edit to the existing message, replacing the values in the message, and also likely includes an ephemeral message
   in the response
1. Users interact with the message
1. eventbot receives interactive message via ``interactive_event_handler`` function and responds back, with
   an edit to the existing message, or a dialog, depending on the action.
'''


from typing import Dict
import logging

import omnibot_receiver.response as omnibot_response
from omnibot_receiver.router import (
    OmnibotMessageRouter,
    OmnibotInteractiveRouter,
    OmnibotRouter,
)

from eventbot.models.event import Event
from eventbot.models.user import User

logger = logging.getLogger(__name__)

message_router = OmnibotMessageRouter(
    help="Hi! I'll help you create and manage events!"
)
interactive_router = OmnibotInteractiveRouter()
router = OmnibotRouter(
    message_router=message_router,
    interactive_router=interactive_router,
)


def _get_user_id_by_event(event: Dict) -> str:
    return event['parsed_user']['id']


def _get_user_by_event(event: Dict):
    try:
        return User.get(_get_user_id_by_event(event))
    except User.DoesNotExist:
        return None


@message_router.route(
    'event create',
    match_type='command',
    help='Create an event',
)
@message_router.route(
    'create',
    match_type='command',
    help='Create an event',
)
def create_event_command(event: Dict) -> Dict:
    '''
    create_event_command receives ``create`` command messages targeted to this bot. It responds with an interactive
    message, with an ``eventbot_events`` callback.

    The passed-in event is unused, but required by the router.
    '''
    return {
        'actions': [
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'thread_ts': None,
                    'attachment_type': 'default',
                    'attachments': [
                        {
                            'callback_id': 'eventbot_events',
                            'title': (
                                'To finalize creation of event, edit its details'
                            ),
                            'actions': [
                                {
                                    'name': 'edit',
                                    'text': 'Edit event details',
                                    'type': 'button',
                                },
                            ],
                        },
                    ],
                },
            },
        ],
    }


def _update_venmo_dialog(event: Dict, venmo_handle: str):
    '''
    Given an omnibot interactive component event, and a venmo_handle, return a response to open an interactive
    dialog, with a venmo_handle prompt. We hide the action and the message id in the state, so that we can
    have this context when parsing the submission later.
    '''
    return {
        'actions': [{
            'action': 'dialog.open',
            'kwargs': {
                'trigger_id': event['trigger_id'],
                'dialog': {
                    'callback_id': 'eventbot_events',
                    'title': 'Update Venmo Handle',
                    'state': f'update_venmo:{event["message_ts"]}',
                    'elements': [
                        {
                            'label': 'Venmo Handle',
                            'name': 'venmo_handle',
                            'type': 'text',
                            'value': f'{venmo_handle}',
                        },
                    ],
                },
            },
        }]
    }


def _edit_event_dialog(
    event: Dict,
    name: str = '',
    description: str = '',
    cost: int = 0,
    extra_attendees: int = 0,
) -> Dict:
    '''
    Given an omnibot interactive component event, and a set of pre-set values, return a submission dialog to edit the
    event. We hide the action and the message id in the state so that we can have this context later, when we receive
    the dialog submission event.
    '''
    return {
        'actions': [{
            'action': 'dialog.open',
            'kwargs': {
                'trigger_id': event['trigger_id'],
                'dialog': {
                    'callback_id': 'eventbot_events',
                    'title': 'Create event',
                    'state': f'update_event:{event["message_ts"]}',
                    'elements': [
                        {
                            'label': 'Event Name',
                            'name': 'name',
                            'type': 'text',
                            'value': name,
                        },
                        {
                            'label': 'Event Description',
                            'name': 'description',
                            'type': 'text',
                            'optional': True,
                            'value': description,
                        },
                        {
                            'label': 'Event Cost',
                            'name': 'cost',
                            'type': 'text',
                            'optional': True,
                            # We're storing the cost in cents, but want to display in dollars and cents
                            'value': f'{cost/100:.2f}',
                        },
                        {
                            'label': 'Extra Attendees',
                            'name': 'extra_attendees',
                            'type': 'text',
                            'optional': True,
                            'hint': (
                                'Number of attendees unable to self-register,'
                                ' or who forgot (used to split cost)'
                            ),
                            'value': str(extra_attendees),
                        },
                    ],
                },
            },
        }]
    }


@interactive_router.route('eventbot_events', event_type='dialog_submission')
def handle_interactive_event_for_events(event: Dict) -> Dict:
    '''
    This function receives interactive component events for the ``eventbot_events`` callback, specifically
    for the type ``dialog_submission``. It determines which type of dialog was submitted and routes it to the
    appropriate internal function, to handle that submission.
    '''
    state = event['state']
    if state.startswith('update_venmo:'):
        return _update_venmo_via_event(event)
    elif state.startswith('update_event:'):
        return _create_or_edit_event(event)
    # backwards compat: raw event_id
    else:
        return _create_or_edit_event(event)


def _update_venmo(user_id: str, venmo_handle: str) -> Dict:
    try:
        user = User.get(user_id)
    except User.DoesNotExist:
        user = User(user_id=user_id)
    user.venmo_handle = venmo_handle
    try:
        user.save()
    except Exception:
        logger.exception(f'Failed to save venmo for user <@{user_id}>')
        return False
    return True


def _update_venmo_via_event(event: Dict) -> Dict:
    # TODO (ryan-lane): support more than just venmo
    user_id = _get_user_id_by_event(event)
    submission = event.get('submission', {})
    if 'venmo_handle' not in submission:
        msg = 'Error: venmo_handle missing from form submission.'
        return omnibot_response.get_simple_response(msg, ephemeral=True)
    venmo_handle = submission['venmo_handle']
    venmo_updated = _update_venmo(user_id, venmo_handle)
    if not venmo_updated:
        msg = 'Failed to save venmo handle'
        return omnibot_response.get_simple_response(msg, ephemeral=True)
    msg = 'Successfully saved venmo handle.'
    event_id = event['state'].replace('update_venmo:', '')
    try:
        event_obj = Event.get(event_id)
        ret = omnibot_response.get_simple_response(msg, ephemeral=True)
    except Event.DoesNotExist:
        msg = f'{msg}. However, we could not find the related event; please update manually.'
        ret = omnibot_response.get_simple_response(msg, ephemeral=True)
    ret['actions'] = [{
        'action': 'chat.update',
        'kwargs': _get_event_kwargs(
            event_id,
            event['channel']['id'],
            event_obj,
        ),
    }]
    return ret


def _create_or_edit_event(event: Dict) -> Dict:
    if event['state'].startswith('update_event:'):
        event_id = event['state'].replace('update_event:', '')
    # backwards compat: raw event_id
    else:
        event_id = event['state']
    submission = event.get('submission', {})
    name = submission['name']
    description = submission.get('description', '')
    extra_attendees = int(submission.get('extra_attendees', 0))
    cost = int(float(submission.get('cost', 0)) * 100)

    try:
        event_obj = Event.get(event_id)
    except Event.DoesNotExist:
        event_obj = Event(event_id)
        event_obj.creator = event['parsed_user']['id']
    event_obj.name = name
    event_obj.description = description
    event_obj.extra_attendees = extra_attendees
    event_obj.cost = cost
    try:
        event_obj.save()
    except Exception:
        logger.exception('Failed to create event')
        msg = 'Failed to create event'
        return omnibot_response.get_simple_response(msg, ephemeral=True)
    ret = {
        'actions': [{
            'action': 'chat.update',
            'kwargs': _get_event_kwargs(
                event_id,
                event['channel']['id'],
                event_obj,
            ),
        }],
    }
    return ret


@interactive_router.route('eventbot_events')
def interactive_event_handler(event: Dict) -> Dict:
    '''
    This function receives interactive component events for callback ``eventbot_events``, without a specific
    event type. In this bot's context, this function is routed to when a user clicks on any button in the
    interactive message. It determines the action (edit, register, unregister, etc.) and calls the appropriate
    internal function.
    '''
    user_id = _get_user_id_by_event(event)
    venmo_handle = ''
    try:
        user = User.get(user_id)
        if user.venmo_handle:
            venmo_handle = user.venmo_handle
    except User.DoesNotExist:
        pass
    for action in event.get('actions', []):
        event_action = action.get('name')
        if not event_action:
            msg = 'Missing value or text in interactive component event'
            return omnibot_response.get_simple_response(msg, ephemeral=True)
        if event_action == 'edit':
            return _edit_event_dialog(event)
        event_id = action.get('value')
        if not event_id:
            msg = 'Missing value or text in interactive component event'
            return omnibot_response.get_simple_response(msg, ephemeral=True)
        event_id = event_id.lower()
        try:
            event_obj = Event.get(event_id)
        except Event.DoesNotExist:
            msg = f'Event with event_id {event_id} does not exist.'
            return omnibot_response.get_simple_response(msg, ephemeral=True)
        if event_action == 'register':
            ret = _register_event(event_obj, user_id)
        elif event_action == 'unregister':
            ret = _unregister_event(event_obj, user_id)
        elif event_action == 'update':
            # This event triggers a dialog open, but doesn't directly update
            # the event, so we should return immediately.
            return _edit_event_dialog(
                event,
                event_obj.name,
                event_obj.description,
                event_obj.cost,
                event_obj.extra_attendees,
            )
        elif event_action == 'update_venmo':
            return _update_venmo_dialog(event, venmo_handle)
        elif event_action == 'refresh':
            # Just update the event
            pass
        else:
            msg = 'Unrecognized action'
            return omnibot_response.get_simple_response(msg, ephemeral=True)
        ret['actions'] = [
            {
                'action': 'chat.update',
                'kwargs': _get_event_kwargs(
                    event_id,
                    event['channel']['id'],
                    event_obj,
                ),
            },
        ]
        # We only ever expect to get a single action from an event, so we
        # return in the first loop iteration
        return ret
    msg = f'Missing actions in interactive event'
    return omnibot_response.get_simple_response(msg, ephemeral=True)


def _register_event(event_obj: Event, attendee: str) -> Dict:
    if event_obj.user_is_attendee(attendee):
        msg = f'<@{attendee}> already registered'
    else:
        event_obj.add_attendee(attendee)
        try:
            event_obj.save()
            msg = f'Registered <@{attendee}>'
        except Exception:
            msg = f'Failed to register <@{attendee}>'
    return omnibot_response.get_simple_response(msg, ephemeral=True)


def _unregister_event(event_obj: Event, attendee: str) -> Dict:
    if event_obj.user_is_attendee(attendee):
        event_obj.remove_attendee(attendee)
        try:
            event_obj.save()
            msg = f'Unregistered <@{attendee}>'
        except Exception:
            msg = f'Failed to unregister <@{attendee}>'
    else:
        msg = f'<@{attendee}> not registered.'
    return omnibot_response.get_simple_response(msg, ephemeral=True)


def _get_event_kwargs(event_id: str, channel_id: str, event_obj: Event) -> Dict:
    '''
    Given an event_id, channel_id, and event_obj (pynamo model), return the event, represented as a slack
    interactive message.
    '''
    cost_text = (
        f'Total cost: ${event_obj.cost/100:.2f}; Cost per attendee:'
        f' ${event_obj.cost_per_attendee/100:.2f}'
    )
    _attendees_with_payment = []
    _attendees_without_payment = []
    if event_obj.attendees:
        attendees = [x.attendee for x in event_obj.attendees]
        users = User.batch_get(attendees)
        for user in users:
            if user.venmo_handle:
                _attendees_with_payment.append(user.venmo_handle)
            else:
                _attendees_without_payment.append("<@{}>".format(user.user_id))
    if _attendees_with_payment:
        attendees_with_payment_text = ', '.join(_attendees_with_payment)
    else:
        attendees_with_payment_text = 'None'
    if _attendees_without_payment:
        attendees_no_payment_text = ', '.join(_attendees_without_payment)
    else:
        attendees_no_payment_text = 'None'
    return {
        'thread_ts': event_id,
        'ts': event_id,
        'text': f'Event *{event_obj.name}*',
        'channel': channel_id,
        'attachment_type': 'default',
        'attachments': [
            {
                'callback_id': 'eventbot_events',
                'fields': [
                    {
                        'title': 'Description',
                        'value': f'{event_obj.description}',
                    },
                    {
                        'title': 'Total attendees',
                        'value': str(event_obj.total_attendees),
                    },
                    {
                        'title': 'Attendee Venmo handles',
                        'value': attendees_with_payment_text,
                    },
                    {
                        'title': 'Attendees missing Venmo handle',
                        'value': attendees_no_payment_text,
                    },
                    {
                        'title': 'Cost',
                        'value': cost_text,
                    },
                    {
                        'title': 'Extra attendees',
                        'value': f'{event_obj.extra_attendees}',
                    },
                ],
                'actions': [
                    {
                        'name': 'update',
                        'text': 'Update event details',
                        'type': 'button',
                        'value': f'{event_id}',
                    },
                    {
                        'name': 'refresh',
                        'text': 'Refresh event details',
                        'type': 'button',
                        'value': f'{event_id}',
                    },
                ],
            },
            {
                'callback_id': 'eventbot_events',
                'title': 'Manage your registration',
                'actions': [
                    {
                        'name': 'register',
                        'text': 'Register',
                        'type': 'button',
                        'value': f'{event_id}',
                    },
                    {
                        'name': 'unregister',
                        'text': 'Unregister',
                        'type': 'button',
                        'value': f'{event_id}',
                    },
                    {
                        'name': 'update_venmo',
                        'text': 'Update Venmo',
                        'type': 'button',
                        'value': f'{event_id}',
                    },
                ],
            },
        ],
    }
