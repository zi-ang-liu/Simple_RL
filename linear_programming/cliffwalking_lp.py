'''solving the cliff walking problem using linear programming'''
from gurobipy import GRB, Model, quicksum
import gymnasium as gym
import numpy as np
from lp_solver import lp_solver

if __name__ == '__main__':

    # create an environment
    env = gym.make('CliffWalking-v0')
    n_state = env.unwrapped.nS
    n_action = env.unwrapped.nA
    state_set = set(range(n_state))
    action_set = set(range(n_action))
    # The player cannot be at the cliff, nor at the goal 
    terminal_state_set = [47] 
    unreachable_state_set = [37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
    # the reachable state set is the set of all states except the cliff and the goal.
    # only the states in the reachable state set are considered in the optimization problem
    reachable_state_set = set(set(state_set) - set(terminal_state_set) - set(unreachable_state_set))

    # set parameters
    gamma = 1

    # initialize reward and transition probability
    r = np.zeros((n_state, n_action))
    p = np.zeros((n_state, n_action, n_state))

    for state in reachable_state_set:
        for action in action_set:
            for prob, next_state, reward, terminated in env.unwrapped.P[state][action]:
                r[state, action] += prob * reward
                p[state, action, next_state] += prob

    # solve the mdp problem using linear programming
    model = lp_solver(r, p, gamma)

    # state value
    value_function = {}
    for state in reachable_state_set:
        value_function[state] = model.getVarByName(f'v_{state}').x

    policy = {}
    for state in terminal_state_set:
        value_function[47] = 0
        
    for state in reachable_state_set:
        q_max_value = -np.inf
        for action in action_set:
            q_value_temp = sum([prob * (reward + gamma * value_function[next_state])
                             for prob, next_state, reward, terminated in env.unwrapped.P[state][action]])
            if q_value_temp > q_max_value:
                q_max_value = q_value_temp
                policy[state] = action
            
    # print value function 4*12, 1 digital after decimal point

    print('value function = ')
    for i in range(4):
        for j in range(12):
            if i * 12 + j in value_function:
                print('{:.1f}'.format(value_function[i * 12 + j]), end='\t')
            else:
                print('x', end='\t')
        print()

    print('optimal policy = ')
    for i in range(4):
        for j in range(12):
            if i * 12 + j in policy:
                print(policy[i * 12 + j], end='\t')
            else:
                print('x', end='\t')
        print()

    model.write("model.lp")
