import os, random, re
import time
from django.contrib.staticfiles.templatetags.staticfiles import static
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Aaron Yao-Smith'

doc = """
Incentive Compatible Disclosure Study
"""


def make_Likert_agreement(label):
    return models.IntegerField(
        choices=[
            [7, "Strongly agree"],
            [6, "Agree"],
            [5, "Somewhat agree"],
            [4, "Neither agree nor disagree"],
            [3, "Somewhat disagree"],
            [2, "Disagree"],
            [1, "Strongly disagree"]
        ],
        label=label,
        widget=widgets.RadioSelect
    )


class Constants(BaseConstants):
    name_in_url = 'study'
    players_per_group = 6
    num_rounds = 1
    base_reward = c(1)  # base reward for completing the survey
    # estimator_bonus = c(2)  # received if estimate within 10 of answer
    # advisor_bonus = c(2)  # received if estimate > answer
    # advisor_big_bonus = c(4)  # received if estimate >= answer + 100

    # New PayOffs - estimator
    estimator_bonus_less_than_neg_40 = c(0)
    estimator_bonus_within_neg_40_and_31 = c(1)
    estimator_bonus_within_neg_30_and_21 = c(1.5)
    estimator_bonus_within_neg_20_and_11 = c(2)
    estimator_bonus_within_neg_10_and_1 = c(5)
    estimator_bonus_within_0_and_10 = c(5)
    estimator_bonus_within_11_and_21 = c(2)
    estimator_bonus_within_21_and_30 = c(1.5)
    estimator_bonus_within_31_and_40 = c(1)
    estimator_bonus_greater_than_40 = c(0)

    # New PayOffs - advisor
    advisor_bonus_less_than_neg_40 = c(0)
    advisor_bonus_within_neg_40_and_31 = c(0)
    advisor_bonus_within_neg_30_and_21 = c(0)
    advisor_bonus_within_neg_20_and_11 = c(0)
    advisor_bonus_within_neg_10_and_1 = c(0)
    advisor_bonus_within_0_and_10 = c(0.5)
    advisor_bonus_within_11_and_21 = c(1)
    advisor_bonus_within_21_and_30 = c(1.5)
    advisor_bonus_within_31_and_40 = c(2)
    advisor_bonus_greater_than_40 = c(5)

    appeal_reward = c(2)  # given to estimator on appeal win
    appeal_reward_split = appeal_reward / 2  # given to both estimator and advisor if appeal lost or no appeal
    appeal_cost = c(0.25)  # cost of appeal to estimator


class Subsession(BaseSubsession):
    def creating_session(self):
        print("Creating session.")
        # randomize players in groups, then assign disclosure/non-disclosure randomly to groups
        for group in self.get_groups():
            players = group.get_players()
            for p in players:
                print(p.role())
            # random.shuffle(players
            group.set_players(players)
            # group.disclosure = random.choice([True, False])
            group.choose_grid()


class Group(BaseGroup):

    def shuffle_choices(choices):
        print("In shuffle_choice method")
        random.shuffle(choices)
        return choices

    disclosure = models.BooleanField(initial=True)
    appealed = models.BooleanField(
        label="Would you like to send the case to the judge?",
        choices=shuffle_choices([
            [True, "Yes"],
            [False, "No"]
        ]),
        widget=widgets.RadioSelect
    )  # did estimator appeal?
    appeal_granted = models.BooleanField(
        label="As judge, I determine that the " + str(Constants.appeal_reward) + " bonus shall be awarded as follows:",
        choices=shuffle_choices([
            [False, "The estimator and advisor shall both receive " + str(Constants.appeal_reward_split) + "."],
            [True, "The estimator shall receive " + str(Constants.appeal_reward) +
             " and the advisor shall receive nothing."],
        ]),
        widget=widgets.RadioSelect
    )
    recommendation = models.IntegerField(
        min=0,
        max=900,
    )
    estimate = models.IntegerField(
        min=0,
        max=900,
    )

    grid_number = models.IntegerField()
    correct_answer = models.IntegerField()
    grid_path = models.StringField()
    small_grid_path = models.StringField()

    example_grid_number = models.IntegerField()
    example_grid_path = models.StringField()
    example_small_grid_path = models.StringField()

    # Likert scale questions
    e1 = make_Likert_agreement("I blame myself for my guess.")
    e2 = make_Likert_agreement("I blame my advisor for my guess.")
    e3 = make_Likert_agreement("I have a legitimate grievance against my advisor.")
    e4 = make_Likert_agreement("I have a strong case if I chose to pursue an appeal.")
    e5 = make_Likert_agreement("I believe that others would rule in my favor on an appeal.")
    e6 = make_Likert_agreement("My advisor treated me fairly.")
    e7 = make_Likert_agreement("I was mistreated by my advisor.")
    e8 = make_Likert_agreement("I deserve to receive the full bonus of " + str(Constants.appeal_reward) + ".")
    e9 = make_Likert_agreement("My advisor does not deserve to receive " + str(Constants.appeal_reward_split) +
                               " of the bonus.")
    j1 = make_Likert_agreement("I blame the estimator for his/her estimate.")
    j2 = make_Likert_agreement("I blame the advisor for the estimator's estimate.")
    j3 = make_Likert_agreement("The estimator has a legitimate grievance against the advisor.")
    j4 = make_Likert_agreement("The estimator has a strong case if he/she chooses to pursue an appeal.")
    j5 = make_Likert_agreement("I believe that others would rule in the estimator's favor on an appeal.")
    j6 = make_Likert_agreement("The advisor treated the estimator fairly.")
    j7 = make_Likert_agreement("The estimator was mistreated by the advisor.")
    j8 = make_Likert_agreement(
        "The estimator deserves to receive the full bonus of " + str(Constants.appeal_reward) + ".")
    j9 = make_Likert_agreement("The advisor does not deserve to receive " + str(Constants.appeal_reward_split) +
                               " of the bonus.")
    a1 = make_Likert_agreement("I blame the estimator for his/her estimate.")
    a2 = make_Likert_agreement("I blame myself, the advisor, for the estimator's estimate.")
    a3 = make_Likert_agreement("The estimator has a legitimate grievance against me, the advisor.")
    a4 = make_Likert_agreement("The estimator has a strong case if he/she chooses to pursue an appeal.")
    a5 = make_Likert_agreement("I believe that others would rule in the estimator's favor on an appeal.")
    a6 = make_Likert_agreement("I, the advisor treated the estimator fairly.")
    a7 = make_Likert_agreement("The estimator was mistreated by me, the advisor.")
    a8 = make_Likert_agreement(
        "The estimator deserves to receive the full bonus of " + str(Constants.appeal_reward) + ".")
    a9 = make_Likert_agreement("I, the advisor, do not deserve to receive " + str(Constants.appeal_reward_split) +
                               " of the bonus.")

    estimator_opposite_appeal_payoff = models.CurrencyField(initial=c(0))

    # Calculates rewards based on the advisor's recommendation and estimator's estimate, then stores them per player
    # in grid_reward.
    def calculate_grid_rewards(self):
        advisor = self.get_player_by_role('advisor')
        estimator = self.get_player_by_role('estimator')

        # advisor and estimator grid rewards
        print(type(advisor))
        print(type(estimator))
        # if advisor.recommendation >= (self.correct_answer + 100):
        #     advisor.grid_reward = Constants.advisor_big_bonus
        # elif advisor.recommendation > self.correct_answer:
        #     advisor.grid_reward = Constants.advisor_bonus
        # else:
        #     advisor.grid_reward = c(0)
        if estimator.estimate < (self.correct_answer - 40):
            estimator.grid_reward = c(0)  # Nothing
            advisor.grid_reward = c(0) # Nothing
        elif (self.correct_answer - 40) <= estimator.estimate <= (self.correct_answer - 31):
            estimator.grid_reward = c(1)
            advisor.grid_reward = c(0)  # Nothing
        elif (self.correct_answer - 30) <= estimator.estimate <= (self.correct_answer - 21):
            estimator.grid_reward = c(1.5)
            advisor.grid_reward = c(0)  # Nothing
        elif (self.correct_answer - 20) <= estimator.estimate <= (self.correct_answer - 11):
            estimator.grid_reward = c(2)
            advisor.grid_reward = c(0)  # Nothing
        elif (self.correct_answer - 10) <= estimator.estimate <= (self.correct_answer - 1):
            estimator.grid_reward = c(5)
            advisor.grid_reward = c(0)  # Nothing
        elif (self.correct_answer + 0) <= estimator.estimate <= (self.correct_answer + 10):
            estimator.grid_reward = c(5)
            advisor.grid_reward = c(0.5)
        elif (self.correct_answer + 11) <= estimator.estimate <= (self.correct_answer + 20):
            estimator.grid_reward = c(2)
            advisor.grid_reward = c(1)
        elif (self.correct_answer + 21) <= estimator.estimate <= (self.correct_answer + 30):
            estimator.grid_reward = c(1.5)
            advisor.grid_reward = c(1.5)
        elif (self.correct_answer + 31) <= estimator.estimate <= (self.correct_answer + 40):
            estimator.grid_reward = c(1)
            advisor.grid_reward = c(2)
        elif estimator.estimate > (self.correct_answer + 40):
            estimator.grid_reward = c(0)  # Nothing
            advisor.grid_reward = c(5)


    # Chooses a grid. Will choose a random grid-3x3_grid pair based on what is in the directory. Files must be named
    # in this format: gridX_N.svg and small_gridX.svg, where X is a unique number per grid-3x3_grid pair, and N is
    # the number of filled in dots in the entire grid.
    # Will assign values to group variables: grid_number, correct_answer, grid_path, small_grid_path.
    def choose_grid(self):
        static_dir = './study/static/study'
        static_files = os.listdir(static_dir)
        grid_choices = list(filter(lambda x: re.match(r"grid[0-9]*_[0-9]*\.svg", x), static_files))

        random.shuffle(grid_choices)

        self.grid_path = 'study/' + grid_choices.pop()
        self.grid_number = int(re.search(r"grid([0-9]*)_[0-9]*\.svg", self.grid_path).group(1))
        self.correct_answer = int(re.search(r"grid[0-9]*_([0-9]*)\.svg", self.grid_path).group(1))
        self.small_grid_path = 'study/small_grid' + str(self.grid_number) + '.svg'

        self.example_grid_path = 'study/' + grid_choices.pop()
        self.example_grid_number = int(re.search(r"grid([0-9]*)_[0-9]*\.svg", self.grid_path).group(1))
        self.example_small_grid_path = 'study/small_grid' + str(self.example_grid_number) + '.svg'


class Player(BasePlayer):
    grid_reward = models.CurrencyField(initial=c(0))
    entered_email = models.BooleanField()
    disclosure = models.BooleanField()
    # disclosure = random.choice([True, False])
    # disclosure = False
    email = models.StringField(
        label="Please provide your email address. We will send your payment as an Amazon.com gift card to this " +
              "email address within five business days.",
        blank=True,
        initial=""
    )

    consent18 = models.BooleanField(
        label="I am age 18 or older",
        widget=widgets.RadioSelect
    )
    consentRead = models.BooleanField(
        label="I have read and understand the above information",
        widget=widgets.RadioSelect
    )
    consentWant = models.BooleanField(
        label="I want to participate in this research and continue with this study",
        widget=widgets.RadioSelect
    )

    # Demographic questions
    d1 = models.IntegerField(
        label="What is your gender?",
        choices=[
            [1, 'Male'],
            [2, 'Female']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    d2 = models.IntegerField(
        label="What is your age?",
        min=18,
        max=130,
        blank=True
    )
    d3 = models.IntegerField(
        label="What is your race?",
        choices=[
            [1, 'White'],
            [2, 'Black, African-American'],
            [3, 'American Indian or Alaska Native'],
            [4, 'Asian or Asian-American'],
            [5, 'Pacific Islander'],
            [6, 'Some other race']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    d4 = models.IntegerField(
        label="Please indicate the highest level of education completed.",
        choices=[
            [1, 'Grammar school'],
            [2, 'High school or equivalent'],
            [3, 'Vocational/technical school (2 year)'],
            [4, 'Some college'],
            [5, 'College graduate (4 year)'],
            [6, 'Master\'s degree (MS, etc.)'],
            [7, 'Doctoral degree (PhD, etc.)'],
            [8, 'Professional degree (MD, JD, etc.)'],
            [9, 'Other']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    d5 = models.IntegerField(
        label="Please indicate your current household income in U.S. dollars",
        choices=[
            [1, 'Under $10,000'],
            [2, '$10,000 - $19,999'],
            [3, '$20,000 - $29,999'],
            [4, '$30,000 - $39,999'],
            [5, '$40,000 - $49,999'],
            [6, '$50,000 - $74,999'],
            [7, '$75,000 - $99,999'],
            [8, '$100,000 - $150,000'],
            [9, 'Over $150,000']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    recommendation = models.IntegerField(
        min=1,
        max=900,
        initial=None
    )

    # Player based estimate for estimator
    estimate = models.IntegerField(
        min=1,
        max=900,
        initial=None
    )

    # Manipulation checks
    m1 = models.BooleanField(
        label="In the dots-estimation task, the advisor would get a bonus if the estimator overestimated the true number of "
              + "solid dots.",
        widget=widgets.RadioSelect
    )
    m2 = models.BooleanField(
        label="In the dots-estimation task, the estimator would get a bonus if they were within 10 dots of the true number of "
              + "solid dots.",
        widget=widgets.RadioSelect
    )
    m3 = models.BooleanField(
        label="In the dots-estimation task, the estimator was informed that the advisor would make more money if the estimator overestimated "
              + "the true number of solid dots.",
        widget=widgets.RadioSelect
    )

    comment = models.LongStringField(label="Do you have any comments for the researchers? (Optional)", blank=True)

    # def __init__(self):
    #     super().__init__(self)
    #     self.disclosure = random.choice([True, False])
    # define group IDs such that the "advisor" role corresponds to ID==1, "estimator" to ID==2, "judge/judge"
    # to ID==3. Use player.role() to retrieve this role.
    def role(self):
        if self.id_in_group >= 1 and self.id_in_group <= 2:
            return 'advisor'
        elif self.id_in_group >= 3 and self.id_in_group <= 4:
            return 'estimator'
        elif self.id_in_group >= 5 and self.id_in_group <= 6:
            return 'judge'

    def get_correct_answer(self):
        # if(self.is_advisor()):
        #     if(self.disclosure):
        #         #print("In disclosure:advisor")
        #         #print(self.group.correct_answer)
        #         return self.group.correct_answer+92
        #     else:
        #         #print("In non disclosure:advisor")
        #         #print(self.group.correct_answer)
        #         return self.group.correct_answer+29
        # elif(self.is_estimator() or self.is_judge()):
        #     if(self.disclosure):
        #         #print("In disclosure")
        #         print(self.group.correct_answer)
        #         return self.group.correct_answer+100
        #     else:
        #         #print("In non disclosure")
        #         #print(self.group.correct_answer)
        #         return self.group.correct_answer+14
        return self.group.correct_answer

    def set_model_data(self):
        if self.is_advisor():
            print("Advisor recom : ", self.recommendation)
            print(type(self.recommendation))
            if self.recommendation is None or self.recommendation == 0:
                if self.disclosure:
                    print("Set model advisor diclosure")
                    self.recommendation = self.group.correct_answer + 92
                    print("recomm :{0}".format(self.recommendation))
                else:
                    print("Set model advisor non diclosure")
                    self.recommendation = self.group.correct_answer + 29
                    print("recomm nd :{0}".format(self.recommendation))
        elif self.is_estimator():
            if self.recommendation is None or self.estimate == 0:
                if self.disclosure:
                    print("Set model estimator diclosure")
                    self.estimate = self.group.correct_answer + 100
                    print("esti :{0}".format(self.estimate))
                else:
                    print("Set model estimator non diclosure")
                    self.estimate = self.group.correct_answer + 14
                    print("esti nd :{0}".format(self.estimate))
        elif self.is_judge():
            pass

    def is_advisor(self):
        return self.id_in_group in list(range(1, 3))

    def is_estimator(self):
        return self.id_in_group in list(range(3, 5))

    def is_judge(self):
        return self.id_in_group in list(range(5, 7))

    def get_recommendation(self):
        this_player_id = self.id_in_group
        num_players_per_group = Constants.players_per_group / 3
        this_player_id = this_player_id % num_players_per_group
        if this_player_id == 0:
            this_player_id = num_players_per_group
        for player in self.get_others_in_group():
            if ((player.id_in_group) == this_player_id):
                print("returning recommendation : {0}".format(player.recommendation))
                return player.recommendation

    def get_estimate(self):
        this_player_id = self.id_in_group
        num_players_per_group = Constants.players_per_group / 3
        this_player_id = (this_player_id % num_players_per_group)
        if this_player_id == 0:
            this_player_id = num_players_per_group
        # print("player id : "+str(this_player_id))
        if (self.is_estimator()):
            print("Player is an estimator")
            return self.estimate
        elif (self.is_judge()):
            print("From judge info")
            print(this_player_id)
            for player in self.get_others_in_group():
                if ((player.id_in_group) == this_player_id + num_players_per_group):
                    print(player.id_in_group)
                    print(num_players_per_group)
                    return player.estimate
        print(self.is_judge)
        print("Returning none")

    def is_timed_out(self):
        return self.participant.vars['expiry'] - time.time() <= 3

    def calculate_grid_rewards(self):

        corresponding_advisor = None
        for player in self.get_others_in_group():
            if player.id_in_group == (self.id_in_group - (Constants.players_per_group / 3)):
                print(player.id_in_group)
                corresponding_advisor = player

        if corresponding_advisor.recommendation >= (self.get_correct_answer() + 100):
            corresponding_advisor.grid_reward = Constants.advisor_big_bonus
        elif corresponding_advisor.recommendation > self.get_correct_answer():
            corresponding_advisor.grid_reward = Constants.advisor_bonus
        else:
            corresponding_advisor.grid_reward = c(0)

        # estimator reward
        if self.estimate >= (self.get_correct_answer() - 10) and self.estimate <= (self.get_correct_answer() + 10):
            self.grid_reward = Constants.estimator_bonus
        else:
            self.grid_reward = c(0)

    # Assigns rewards to players based on initially calculated grid estimation rewards and appeal results.
    def assign_rewards(self):
        self.payoff = Constants.base_reward + self.grid_reward

        if self.is_advisor():
            if not (self.group.appealed and self.group.appeal_granted):
                self.payoff += Constants.appeal_reward_split

        if self.is_estimator():
            self.group.estimator_opposite_appeal_payoff = self.payoff
            if self.group.appealed:
                self.payoff -= Constants.appeal_cost
            else:
                self.group.estimator_opposite_appeal_payoff -= Constants.appeal_cost

            if self.group.appeal_granted:
                if self.group.appealed:
                    self.payoff += Constants.appeal_reward
                    self.group.estimator_opposite_appeal_payoff += Constants.appeal_reward_split
                else:
                    self.payoff += Constants.appeal_reward_split
                    self.group.estimator_opposite_appeal_payoff += Constants.appeal_reward
            else:
                self.payoff += Constants.appeal_reward_split
                self.group.estimator_opposite_appeal_payoff += Constants.appeal_reward_split
