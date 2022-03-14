import argparse

import examples.ac_for_dac.schedulers


class SchedulerPolicyAction(argparse.Action):
    names = [
        cls.__name__
        for cls in examples.ac_for_dac.schedulers.Serializable.__subclasses__()
    ]

    def __call__(self, parser, namespace, values, option_string=None):
        mapping = dict(
            zip(
                self.names, examples.ac_for_dac.schedulers.Serializable.__subclasses__()
            )
        )
        setattr(namespace, self.dest, mapping[values])


def run_policy(env, policy, instance=None):
    obs = env.reset(instance=instance)
    policy.reset(env.current_instance)
    done = False
    states = []
    rewards = []
    while not done:
        action = policy.act(obs)
        obs, reward, done, _ = env.step(action)
        states.append(obs)
        rewards.append(reward)
    return states, rewards
