import numpy as np


def get_output_sequence_probability_by_forward(output_sequence, init_state_probability,
                                                    transmission_probability,
                                                    reverse_emission_probability):
    current_output_probability = {}

    for current_state, emit_observation_probability in reverse_emission_probability.get(output_sequence[0],
                                                                                        {}).items():
        hidden_state_probability = init_state_probability.get(current_state, -1)
        if hidden_state_probability < 0:
            continue
        current_output_probability[current_state] = hidden_state_probability * emit_observation_probability

    if len(current_output_probability) == 0:
        return 0, 0

    last_words_output_probability = current_output_probability
    next_to_match_index = 1

    for index, output in enumerate(output_sequence[1:], 1):
        current_output_probability = {}
        for current_state, emit_observation_probability in reverse_emission_probability.get(output, {}).items():
            to_current_state_probability = 0
            for last_state, last_probability in last_words_output_probability.items():
                the_transmission_probability = transmission_probability.get(last_state, {}).get(current_state, -1)
                if the_transmission_probability < 0:
                    continue
                print(last_state, current_state, the_transmission_probability)
                to_current_state_probability += last_probability * the_transmission_probability
            if to_current_state_probability != 0:
                current_output_probability[current_state] = to_current_state_probability * emit_observation_probability

        last_words_output_probability = current_output_probability

        if len(current_output_probability) == 0:
            next_to_match_index = index
            break
        else:
            next_to_match_index = index + 1

    return np.sum(list(last_words_output_probability.values())), next_to_match_index


def get_max_probability_states_by_outputs(output_sequence, init_state_probability, transmission_probability,
                                          reverse_emission_probability):
    output_probability_list = []

    current_output_probability = {}
    for current_state, emit_observation_probability in reverse_emission_probability.get(output_sequence[0],
                                                                                        {}).items():
        hidden_state_probability = init_state_probability.get(current_state, -1)
        if hidden_state_probability < 0:
            continue
        current_output_probability[current_state] = (hidden_state_probability * emit_observation_probability, None)

    if len(current_output_probability) == 0:
        return [], 0, 0

    output_probability_list.append(current_output_probability)
    next_process_index = 1

    last_state_output_probability = current_output_probability

    for index, output in enumerate(output_sequence[1:], 1):

        current_state_output_probability = {}

        for current_state, emit_observation_probability in reverse_emission_probability.get(output, {}).items():
            max_to_current_word_probability = 0
            parent_word = None

            for last_state, (last_output_probability, _) in last_state_output_probability.items():

                the_transmission_probability = transmission_probability.get(last_state, {}).get(current_state, -1)
                if the_transmission_probability < 0:
                    continue
                if last_output_probability * the_transmission_probability > max_to_current_word_probability:
                    max_to_current_word_probability = last_output_probability * the_transmission_probability
                    parent_word = last_state

            if max_to_current_word_probability != 0:
                word_output_probability = max_to_current_word_probability * emit_observation_probability
                current_state_output_probability[current_state] = (word_output_probability, parent_word)

        if len(current_state_output_probability) == 0:
            # 匹配失败，返回未匹配的序列的起始位置和已经匹配的结果
            break
        else:
            next_process_index = index + 1
            output_probability_list.append(current_state_output_probability)
            last_state_output_probability = current_state_output_probability

    top_state_output_probability = sorted(last_state_output_probability.items(), key=lambda kv: kv[1][0])[-1]
    # print(top_state_output_probability)
    max_probability_states = []
    max_probability_states.insert(0, top_state_output_probability[0])
    parent_word = top_state_output_probability[1][1]

    for output_probability in reversed(output_probability_list[0:-1]):
        # print(output_probability, output_probability.get(parent_word))
        max_probability_states.insert(0, parent_word)
        parent_word = output_probability.get(parent_word)[1]

    return max_probability_states, top_state_output_probability[1][0], next_process_index
