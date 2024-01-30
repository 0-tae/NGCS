import json
from domain.slack.slack_api import slackAPI


def get_user_name(user_id):
    return slackAPI.get_user_info(user_id, "real_name")


def UTFToKorean(text):
    return text.encode("UTF-8").decode("UTF-8").replace("+", " ")


def UTFToKoreanJSON(data):
    converted_data = json.dumps(data).replace("+", " ")
    return json.loads(converted_data)


def get_dictionary_value_for_depth(keys, dictionary, current_depth):
    if dictionary.get(keys[current_depth]) == None:
        return None

    current_dictionary = dictionary[keys[current_depth]]

    if current_depth == len(keys) - 1:
        return current_dictionary

    return get_dictionary_value_for_depth(keys, current_dictionary, current_depth + 1)


def get_value_from_action(action_dict):
    action_type_dict = {
        "timepicker": ["selected_time"],
        "datepicker": ["selected_date"],
        "static_select": ["selected_option"],
        "users_select": ["selected_user"],
        "plain_text_input": ["value"],
        "checkboxes": ["selected_options"],
        "radio_buttons": ["selected_option", "text", "text"],
        "multi_users_select": ["selected_users"],
        "channels_select": ["selected_channel"],
    }

    keys = action_type_dict[action_dict["type"]]

    # selected_option, text, text
    value = get_dictionary_value_for_depth(
        keys=keys, dictionary=action_dict, current_depth=0
    )

    return value


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)
