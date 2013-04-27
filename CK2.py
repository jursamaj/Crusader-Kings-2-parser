import EasyDialogs
import io
import re

pattI=re.compile(r"^(-?\d+ )+\t*}$")
dataI=re.compile(r"(-?\d+)")
pattF=re.compile(r"^\t*(-?[\d]+.[\d]+ )+\t*$")
dataF=re.compile(r"(-?[\d]+.[\d]+)")

def tick(line):
    tick.count+=1
#    if tick.count>121300:
#    if (tick.count%1000)==0:
#        print tick.count, '>', parse.depth, '>', line
tick.count=0

def noparse(a):
#    parse.depth+=1
    line=''
    while '}' not in line:
        line=a.next().strip()
#        tick(line)
        if '{' in line:
            noparse(a)
#    parse.depth-=1

ignoreThese=['ai', 'army', 'history', 'levy', 'liege_troops', 'owner_troops', 'liege_ships', 'owner_ships', 'controller']

def parse(a):
    parse.depth+=1 ##
    if parse.depth>50:
        assert False, 'too deep'
    line=a.next().strip()
    tick(line) ##
    if line=='':
        return line
    if line=='}':
        return line # end dict
    if line=='{':
        tokens=[u'#', ''] # start unnamed dict
    else:
        tokens=line.split('=')
    if len(tokens)==2:
        if tokens[1]!='':
            if tokens[0] in ignoreThese:
                return ['ignore', tokens[0]]
            tokens[1]=tokens[1].strip('"')
            return tokens # tokens == key, value
        else:
            # tokens == key, ''; start a dict
            if line!='{':
                line=a.next().strip() # eat {
                tick(line) ##
                assert line=='{', 'Expected {, got: %s' % line
                    # error
            if tokens[0] in ignoreThese:
                noparse(a)
#                if tick.count>534000:#
#                    print '[ignore]', tokens[0]#
                return ['ignore', tokens[0]]
            temp=dict()
            while True:
                x=parse(a)
#                print tokens
                parse.depth-=1 ##
                if x=='':
                    continue
                if x=='}':
                    return [tokens[0], temp]
                if x[0]=='ignore':
                    if x[0] not in temp:
                        temp[x[0]]=set()
                    temp[x[0]].add(x[1])
                    continue
                if x[0]=='_i':
                    return [tokens[0], x[1]]
                if x[0]=='_f':
                    line=a.next().strip() # eat {
                    tick(line) ##
                    assert line=='}', 'Expected }, got: %s' % line
                        # error
                    return [tokens[0], x[1]]
                if x[0] in temp: # add value to existing key
                    if isinstance(temp[x[0]], list):
                        temp[x[0]].append(x[1])
                    else:
                        temp[x[0]]=[temp[x[0]], x[1]]
                else: # add pair to temp
                    temp[x[0]]=x[1]
    elif pattI.match(tokens[0]): # string of ints and }
        temp=[u'_i', dataI.findall(tokens[0])]
        return temp
    elif pattF.match(tokens[0]+' '): # string of ints and }
        temp=[u'_f', dataF.findall(tokens[0])]
        return temp

    print line
    line=a.next().strip()
    print line
    line=a.next().strip()
    print line
    line=a.next().strip()
    print line
    line=a.next().strip()
    print line
    assert False, 'Bad line: $%s$' % line
        #error

parse.depth=0 ##

#readName=EasyDialogs.AskFileForOpen(wanted=str)
readName='/Users/jerrybarrington/Documents/Paradox Interactive/Crusader Kings II/save games/autosave.ck2'
readFile=io.open(readName,'rt',1,'latin_1')
lines=readFile.readlines()
readFile.close()
print 'file:', readName
print 'lines in file:', len(lines)

lines.insert(0,'root=')
lines.insert(1,'{')
#lines.extend('}')
#lines.extend('}')
#lines.extend('}')
a=iter(lines)

root=parse(a)
parse.depth-=1 ##

root=root[1]

n='0123456789'

keys=set(root.keys())
print 'root keys:', len(keys)

# root['rel_999'] # for character 999's relationships to others (opinion modifiers)
relationships=set(x for x in keys if x.startswith('rel_'))
keys-=relationships
print 'relationships:', len(relationships)

# root['999'] # for province # 999 (1..929)
patt=re.compile(r"^\d+$")
provinces=set(x for x in keys if patt.match(x))
keys-=provinces
print 'provinces:', len(provinces)
provinceNames=set(root[x]['name'] for x in provinces)

# root['polity_key'] # starts with [bcdke]_
# [b*=2795, c*=924, d*=384, k*=88, e*=17]=4208
patt=re.compile(r"^[bcdke]_")
polities=set(x for x in keys if patt.match(x))
keys-=polities
print 'polities', len(polities)

# root['diplo_999'] # for character 999's diplomacy
patt=re.compile(r"^diplo_")
diplo=set(x for x in keys if patt.match(x))
keys-=diplo
print 'diplo:', len(diplo)

# root['religion_name'] # 24 religions
religions=set(x for x in keys if 'authority' in root[x])
keys-=religions
print 'religions:', len(religions)

# everything else (23):  active_objective, active_war, character,
# character_action, character_history, combat, date, delayed_event,
# diplomacy, dynasties, flags, id, income_statistics, nation_size_statistics,
# next_outbreak_id, player, player_realm, rebel, start_date, sub_unit, unit,
# version, war
print 'misc:', keys

# root['dynasties']['999'] # for dynasty 999
dynasties=root['dynasties'].keys()
print 'dynasties:', len(dynasties)

# root['character']['999'] # for character 999
characters=root['character'].keys()
live_characters=[x for x in characters if 'death_date' not in root['character'][x]]
employed_characters={x:root['character'][x]['employer'] for x in live_characters if 'employer' in root['character'][x]}
print 'characters:', len(characters)
test=root['character'][root['player']['id']]['dynasty']
for x in characters:
    if root['character'][x]['dynasty']==test:
        root['character'][x]['birth_name']=root['character'][x]['birth_name']+'*'
dynasts=set(x for x in live_characters if root['character'][x]['dynasty']==test)
dynasts_women=set(x for x in dynasts if root['character'][x].get('female')=='yes')
date=root['date']
date=date.partition('.')
lower=str(int(date[0])-6)+'.'+date[2]
upper=str(int(date[0])-45)+'.'+date[2]
dynasts_marriageable=set(x for x in dynasts_women if lower>=root['character'][x]['birth_date']>=upper)

# sum(int(root[x].get('max_settlements') or 0) for x in provinces)
# => 3788 total settlements available

# [root['character'][x]['birth_name'] for x in characters \
#   if root['character'][x]['dynasty']=='9208' and 'death_date' \
#   not in root['character'][x]]
# => names of all living members of my dynasty (9208)

# [(root['character'][x]['birth_name'], root['character'][x]['claim']) \
#   for x in characters if 'host' in root['character'][x] and \
#   root['character'][x]['host']=='512152' and 'claim' in root['character'][x]]
# => all claims by members of my court

# [(root['character'][x]['birth_name'], root['character'][x]['dynasty'], root['character'][x]['female']) for x in characters if ('host' in root['character'][x] and root['character'][x]['host']=='512152' and 'claim' in root['character'][x]) or root['character'][x]['dynasty']=='9208' and 'death_date' not in root['character'][x]]
# name/dynasty/sex of all in my dynasty or my employees

print

held_polities=set(x for x in polities if 'holder' in root[x])
sub_polities=set(x for x in polities if 'liege' in root[x])
# held_polities-sub_polities => independent realms
my_domain=set()
me=root['player']['id']
temp=set(x for x in held_polities if root[x]['holder']==me)
while len(temp)>0:
    test=temp.pop()
    my_domain.add(test)
    temp2=set(x for x in sub_polities if root[x]['liege']==test)
    temp|=temp2
    temp-=my_domain
print 'My domain:', len(my_domain), 'polities'
# All polities in my domain.

my_vassals=set(root[x]['holder'] for x in my_domain)
print 'My vassals', len(my_vassals), 'landed people, including me'
# All rulers in my domain, including me.

courtiers=set(x for x in employed_characters if employed_characters[x] in my_vassals)
courtiers-=my_vassals
print 'All courts:', len(courtiers), 'unlanded courtiers, excluding vassals/prisoners/wards'
# Includes all unlanded members of courts, even if abroad, except vassals, prisoners, wards.
# Vassals in my_vassals.  Prisoners/wards can't be invited/granted.
# Prisoners/wards can be found with 'host' instead of 'employer'. (Can marry them.)

court=set(x for x in employed_characters if employed_characters[x]==me)
court-=my_vassals
print 'My court:', len(court)
# My immediate court.

all_claimants=set(x for x in live_characters if 'claim' in root['character'][x])
# global character has any claims
print 'All claimants:', len(all_claimants)

vassal_claimants=set(x for x in my_vassals if 'claim' in root['character'][x])
# vassal character has any claims
print 'Vassal claimants:', len(vassal_claimants)

courtier_claimants=set(x for x in courtiers if 'claim' in root['character'][x])
# courtier character has any claims
print 'Courtier claimants:', len(courtier_claimants)

# promote single claim dict to list of dict
for x in all_claimants:
    if isinstance(root['character'][x]['claim'],dict):
        root['character'][x]['claim']=[root['character'][x]['claim']]

claim_type={'yes':{'yes':'w+', 'no':'w-'}, 'no':{'yes':'s+', 'no':'s-'}}
sex={'no':'m', 'yes':'f'}
vassal={True:'v', False:'c'}
mine={True:'y', False:'n'}
claimants=vassal_claimants|courtier_claimants
print
print 'claimants in my realm'
print 'char#,char name,female,vassal,type,level,title,mine'
for x in claimants:
    prefix=x+ ','+ root['character'][x]['birth_name']+ ','+ \
            sex[root['character'][x].get('female','no')]+ ','+ \
            vassal[x in vassal_claimants]
    for y in root['character'][x]['claim']:
        print prefix+','+ claim_type[y['weak']][y['pressed']]+','+ \
              y['title'][0]+','+ y['title']+','+ mine[y['title'] in my_domain]

print
print 'my dynasts out of my realm'
loose_dynasts=(dynasts-my_vassals)-courtiers
for x in loose_dynasts:
    if 'liege' in root['character'][x]:
        host=root['character'][x]['liege']
        liege_flag='*'
    else:
        host=root['character'][x]['host']
        liege_flag=''
    print x+ ','+ root['character'][x]['birth_name']+ ','+ \
          sex[root['character'][x].get('female','no')]+ ',x,,,'+ \
          root['character'][host]['demesne']['capital']+ liege_flag

global_holdings=set(x for x in held_polities if x[0]=='b')
test=root['player']['id']
scan=range(24)
print
print 'tech in my demesne'
my_holdings=set(x for x in global_holdings if root[x]['holder']==test)
my_provinces=set(x for x in provinces if len(set(root[x].keys()) & my_holdings)>0)
for x in my_provinces:
    tech=[int(root[x]['technology']['level'][pos]+root[x]['technology']['progress'][pos])/10.0 for pos in scan]
    print root[x]['name']+ ','+ `tech`.translate(None,'[ ]')
print
print 'tech in my realm'
vassal_holdings=set(x for x in global_holdings if root[x]['holder'] in my_vassals)
other_holdings=global_holdings-vassal_holdings
vassal_provinces=set(x for x in provinces if len(set(root[x].keys()) & vassal_holdings)>0)
for x in vassal_provinces:
    tech=[int(root[x]['technology']['level'][pos]+root[x]['technology']['progress'][pos])/10.0 for pos in scan]
    print root[x]['name']+ ','+ `tech`.translate(None,'[ ]')+ ','+ n[len(set(root[x].keys()) & vassal_holdings)]+ ','+ n[len(set(root[x].keys()) & other_holdings)]
# province name, [tech*24], vassal holdings, foreign holdings

# foreign provinces my realm has holdings in
foreign_holdings=set((x, root[x]['title']) for x in vassal_provinces if root[root[x]['title']]['holder'] not in my_vassals)
# process: q,r=foreign_holdings.pop()

# all provinces my realm has holdings in, & number of holdings
realm_provinces=[[root[x]['name'], len(set(root[x].keys()) & vassal_holdings)] for x in vassal_provinces]
alien_provinces=[[root[x]['name'], len(set(root[x].keys()) & other_holdings)] for x in vassal_provinces]

print
best_tech=[0.0]*24
for x in provinces:
    for pos in scan:
        tech=int(root[x]['technology']['level'][pos]+root[x]['technology']['progress'][pos])/10.0
        if tech>best_tech[pos]:
            best_tech[pos]=tech
print 'world max,'+`best_tech`.translate(None,'[ ]')

# q={'ignore': set([u'liege_troops'])}
# [x for x in held_polities if 'liege' in root[x] and root['character'][root[x]['holder']]['demesne']==q]
# should catch vassal mercenaries

# mercs, holy orders, and religious heads
unlanded_polities=[x for x in held_polities if root[x].get('de_jure_liege','')=="---" and root[x]['succession']=='open_elective']
unlanded_rulers={root[x]['holder']:x for x in unlanded_polities}
u_r_courtiers=[x for x in employed_characters if employed_characters[x] in unlanded_rulers]
print
print 'unlanded polities, rulers, and their courtiers:', len(unlanded_polities), len(unlanded_rulers), len(u_r_courtiers)
print 'the courtiers:'
for x in u_r_courtiers:
    emp=employed_characters[x]
    if x<>emp:
        emp_polity=unlanded_rulers[emp]
        print x+','+root['character'][x]['birth_name']+','+sex[root['character'][x].get('female','no')]+','+emp+','+root['character'][emp]['birth_name']+','+unlanded_rulers[emp]

# unlanded rulers with land:
# [(x,unlanded_rulers[x],root['character'][x]['demesne']) for x in unlanded_rulers if 'capital' in root['character'][x]['demesne']]
# ... if 'liege' not in root[x]?
# ... if 'de_jure_law_changer' not in root[x]?

# my domain minus me & barons
# a=set(x for x in my_domain if root[x]['holder']<>me and x[0]<>'b')
# name, polity, and de jure leige
# b=[(root['character'][root[x]['holder']]['birth_name'],x,root[x].get('de_jure_liege','XXX')) for x in a if root[root[x]['liege']]['holder']==me and root[root[x]['liege']]['holder']<>root[root[x].get('de_jure_liege','xxx')]['holder']]

# sub-polities with a de jure liege
# q=[x for x in sub_polities if 'de_jure_liege' in root[x]]
# ... that isn't their current liege
# r=[x for x in q if root[x]['de_jure_liege']==root[x]['liege']]


# weights for different techs (pref. int; 0=don't care[inadvisable], higher=more interest)
tech_interest=[ 1,  1,  1,  1,  1,  2, 10,  7,
                3,  7,  5,  7,  4,  4,  4,  2,
                3,  3,  3,  1,  1,  7,  7, 10]

def tech(target):
    t=[0]*24
    for x in scan:
        if root[target]['technology']['level'][x]>capital_tech[x]:
            t[x]=tech_interest[x]*capital_progress[x]
    return [sum(t)]+t

capital_barony=root['character'][me]['demesne']['capital']
capital_province=[x for x in provinces if capital_barony in root[x]][0]
capital_tech=root[capital_province]['technology']['level']
capital_progress=[2520/(10-int(x)) for x in root[capital_province]['technology']['progress']]
provinces_with_alien_baronies=[x for x in provinces if 1 in set(1 for y in root[x] if y[0:2]=='b_' and root[y]['holder'] not in my_vassals)]
spy_tech=[(root[x]['name'],tech(x)) for x in provinces_with_alien_baronies]
spy_tech=filter(lambda x:x[1][0]>0,spy_tech)
spy_tech.sort(None,lambda x:x[1][0],True)
print
print 'progress,,'+`[int(x) for x in root[capital_province]['technology']['progress']]`.translate(None,'[ ]')
print 'tech_interest,,'+`tech_interest`.translate(None,'[ ]')
for x in spy_tech:
    print x[0]+','+`x[1]`.translate(None,'[ ]')


# list as string with no space or brackets
# `[1, 2, 3]`.translate(None,'[ ]')

# holdings on main screen = castles + cities + bishoprics
# vassals on load screen = direct vassals, Count and higher
# 'host' whose court they're in at the moment [prison keeper, guardian, court liege]
# 'employer' self if any level ruler, else liege for courtier


great_chars=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
greatest=0
for x in live_characters:
    stats=min(int(a) for a in root['character'][x]['attributes'])
    if stats>greatest:
        greatest=stats
    great_chars[stats].append(x)
print
print "Greatest:", greatest
print "Counts:", [len(x) for x in great_chars]
print "Great chars:", great_chars[greatest]




patt_int=re.compile(r"^\d+$")
patt_fixed=re.compile(r"^\d+.\d\d\d$")
month_days=[31,28,31,30,31,30,31,31,30,31,30,31]

def is_int(str):
    return patt_int.match(str)

def is_fixed(str):
    return patt_fixed.match(str)

def is_a_date(str):
    a=str.split('.')
    if len(a)==3 and is_int(a[0]) and is_int(a[1]) and is_int(a[2]):
        a,b,c=int(a[0]),int(a[1]),int(a[2])
        if a<=1600 and 1<=b<=12 and c<=month_days[b-1]:
            return True
    return False

def flattenTree(tree, x):
    for (key, value) in x.items():
#        print key
#        print value
#        print
        if key in polities:
            key='<polity key>'
#        print type(value)

        if isinstance(value, dict):
#            print 'dict'
            if key not in tree:
                tree[key]=dict()
#            print type(tree[key]), type(value)
            flattenTree(tree[key], value)
        elif isinstance(value, (unicode, str)):
#            print 'str'
            if value in provinceNames:
                value='<province name>'
            elif value in religions:
                value='<religion name>'
            elif value in polities:
                value='<polity key>'
            elif is_int(value):
                if value in characters:
                    value='<character #>'
                elif len(value)==1:
                    value='<digit>'
                else:
                    value='<int value>'
            elif is_fixed(value):
                value='<fixed value>'
            elif is_a_date(value):
                value='<date value>'
            if key not in tree:
                tree[key]=set()
#            print type(tree[key]), type(value)
            tree[key].add(value)
#            print '>', tree[key]
        elif isinstance(value, list):
#            print 'list'
            if isinstance(value[0], (unicode, str)):
                if key not in tree:
                    tree[key]=[]
#                  print type(tree[key]), type(value)
                    for k in range(len(value)):
                        tree[key].append(set(value[k]))
                else:
#                   print type(tree[key]), type(value)
                    for k in range(len(value)):
                        tree[key][k].add(value[k])
            else:
                if key not in tree:
                    tree[key]=dict()
                for k in range(len(value)):
                    flattenTree(tree[key], value[k])
        elif isinstance(value, set):
            if key not in tree:
                tree[key]=set()
            tree[key]|=value
        else: assert False, 'tree error'

tree=dict()
for x in provinces:
    backTree=tree
    backX=x
    flattenTree(tree, root[x])
#    print
#    break
#print tree
print
