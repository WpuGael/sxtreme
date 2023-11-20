from discord.utils import get
import random

def has_perms(guild, member, min_role):
	min_role = get(guild.roles, name=min_role)
	return (member.top_role >= min_role)

def format_to_k(amount):
	#takes amount as string from message.content
	#returns an integer in K
	#amount=str(amount)
	try:
		if (amount[-1:]).lower()=="m":
			return int(float(str(amount[:-1]))*1000)
		elif (amount[-1:]).lower()=="k":
			return int(float(str(amount[:-1])))
		elif (amount[-1:]).lower()=="b":
			return int(float(str(amount[:-1]))*1000000)
		else:
			return int(float(amount)*1000)
	except:
		return

def format_from_k(amount, round_k = True):
	#takes amount as integer in K
	#returns a string to be printed
	if round_k:
		if amount >= 1000000:
			if len(str(amount)) == 7:
				return '{0:.3g}'.format(amount * 0.000001) + "B"
			elif len(str(amount)) == 8:
				return '{0:.4g}'.format(amount * 0.000001) + "B"
			else:
				return '{0:.5g}'.format(amount * 0.000001) + "B"
		elif amount >= 1000:
			if len(str(amount)) == 4:
				return '{0:.3g}'.format(amount * 0.001) + "M"
			elif len(str(amount)) == 5:
				return '{0:.4g}'.format(amount * 0.001) + "M"
			elif len(str(amount)) == 6:
				return '{0:.5g}'.format(amount * 0.001) + "M"
		else:
			return str(amount) + "k"
	else:
		return '{:,}'.format(amount * 1000) + " gp"

def scorefp(hand):
    pairs, three = 0, False
    returned = (0, "None")

    for i in hand:
        if hand.count(i) == 5:
            returned=6, "Five Of A Kind"
        elif hand.count(i) == 4:
            returned=5, "Four Of A Kind"

        if hand.count(i) == 3:
            three = True
        if hand.count(i) == 2:
            pairs += 1
        if pairs >= 1 and three:
            returned=4, "Full House"
        elif three:
            returned = 3, "Three Of A Kind"
        elif pairs >= 3:
            returned = 2, "Two Pairs"
        elif pairs == 1 or pairs == 2:
            returned = 1, "One Pair"

    if 7 in hand and 8 in hand:
        return 7, "Two Wild Flowers (Auto-Win)"
    elif 7 in hand or 8 in hand:
        if returned[0] == 6 or returned[0] == 5:
            return 6, "Five Of A Kind"
        elif returned[0] == 4 or returned[0] ==3:
            return 5, "Four Of A Kind"
        elif returned[0] == 2:
            return 4, "Full House"
        elif returned[0] == 1:
            return 3, "Three Of A Kind"
        elif returned[0] == 0:
            return 1, "One Pair"
    else:
        return returned

def pickflower():
	roll=random.randint(0,9990)
	if roll in range(0,10):
		return 8#"White"
	elif roll in range(10,20):
		return 7#"Black"
	elif roll in range(20,1486):
		return 6#"Mixed"
	elif roll in range(1486,2564):
		return 5#"Assorted"
	elif roll in range(2564,4102):
		return 4#"Orange"
	elif roll in range(4102,5587):
		return 3#"Purple"
	elif roll in range(5587,7052):
		return 2#"Yellow"
	elif roll in range(7052,8582):
		return 1#"Blue"
	elif roll in range(8582,9990):
		return 0#"Red"