#!/usr/local/bin/python3

# convert a ged file to json format for interactive sunbust display
#
# v2.0

# input parameters
# 1 = name of ged file
# 2 = operation = "list", "noparents", "json", "generations", "sunburst",
#                 "ancestors", "grandparents",
#                 "problems" or "bloodmarriages"
# 3 = required for "json", "ancestors", "grandparents", or "sunburst":
#     the id of the person for the start of the output
#
# output to stdout

import sys
import os

if len(sys.argv) < 2:
   print( 'Missing file as first parameter', file=sys.stderr )
   sys.exit( 1 )
if len(sys.argv) < 3:
   print( 'Missing operation as second parameter', file=sys.stderr )
   sys.exit( 1 )

datafile  = sys.argv[1]
operation = sys.argv[2].lower().rstrip('s')

selection = None
if len(sys.argv) > 3:
   selection = sys.argv[3]

if not os.path.isfile( datafile ):
   print( 'Data file does not exist.', file=sys.stderr )
   sys.exit( 1 )

def check_selection():
    result = None
    if selection:
      p = int( selection )
      if p in persons:
         result = p
      else:
         print( 'Selected top parent doesn\'t exist ', file=sys.stderr )
    else:
       print( 'Missing number to select top parent', file=sys.stderr )
    return result

def escape_quote( s ):
    return s.replace( '"', '\\"' )

def compact_spaces( s ):
    return ' '.join( s.replace( '\t', ' ' ).strip().split() )

def to_indi( item ):
    return int( item.lower().replace( '@i', '' ).replace( '@', '' ).lstrip( '0' ) )

def to_fam( item ):
    return int( item.lower().replace( '@f', '' ).replace( '@', '' ).lstrip( '0' ) )

def show_person( p, person ):
    name  = ''
    birth = ''
    if 'name' in person:
       name = person['name']
    if 'birth' in person:
       birth = person['birth']

    print( p, name, birth )

def parent_from_family( f, parent ):
    result = None
    if f is not None:
       if f in families:
          if parent in families[f]:
             result = families[f][parent]
    return result

def parent_family_from_person( p ):
    result = None
    if p is not None:
       if p in persons:
          if 'child of' in persons[p]:
             result = persons[p]['child of']
    return result

def find_married_cousins( f ):
    husb = parent_from_family( f, 'husband' )
    wife = parent_from_family( f, 'wife' )
    if husb and wife:
       if husb == wife:
          print( 'Family', f, 'one person', husb, wife )
       else:
          husb_childof = parent_family_from_person( husb )
          wife_childof = parent_family_from_person( wife )
          if husb_childof and wife_childof:
             if husb_childof == wife_childof:
                print( 'Family', f, 'is married sibings', husb, wife )
             else:
                # check both grandparent families
                gpfamilies = []
                gp = parent_family_from_person( parent_from_family( husb_childof, 'husband' ) )
                if gp:
                   gpfamilies.append( gp )
                gp = parent_family_from_person( parent_from_family( husb_childof, 'wife' ) )
                if gp:
                   gpfamilies.append( gp )
                gp = parent_family_from_person( parent_from_family( wife_childof, 'husband' ) )
                if gp:
                   gpfamilies.append( gp )
                gp = parent_family_from_person( parent_from_family( wife_childof, 'wife' ) )
                if gp:
                   gpfamilies.append( gp )
                for gp in gpfamilies:
                    if gpfamilies.count(gp) > 1:
                       print( 'Family', f, 'is married cousins', husb, wife )
                       break

def find_married_own_desc( target, generation, p ):
    for f in persons[p]['families']:
        for child in families[f]['children']:
            if target == child:
               desc = 'gg+child'
               if generation == 0:
                  desc = 'child'
               if generation == 1:
                  desc = 'grandchild'
               print( 'Person', target, 'married own', desc, child )
               find_married_own_desc( target, generation+1, child )

def find_fam_problems( f, family ):
    if 'husband' in family and 'wife' in family:
       if family['husband'] == family['wife']:
          print( 'Family', f, 'husband and wife are same person' )

    for child in family['children']:
        if 'husband' in family and child == family['husband']:
           print( 'Family', f, 'has a child as the husband' )
        if 'wife' in family and child == family['wife']:
           print( 'Family', f, 'has a child as the wife' )
        if family['children'].count(child) > 1:
           print( 'Family', f, 'has duplicated children' )

def find_problems( p ):
    # if in more than one family, will also detect loops

    first = None

    for f in families:
        for child in families[f]['children']:
            if p == child:
               if first:
                  print( 'Person', p, 'child of families', first, 'and', f )
               else:
                  first = f

def ancestors( indent, gen, max_gen, p ):
    if gen < max_gen:
       name = 'unknown'
       if 'name' in persons[p]:
          name = persons[p]['name']

       print( indent + str(p), name )

       f = parent_family_from_person( p )
       if f:
          husb = parent_from_family( f, 'husband' )
          if husb:
             ancestors( indent + '  ', gen+1, max_gen, husb )
          wife = parent_from_family( f, 'wife' )
          if wife:
             ancestors( indent + '  ', gen+1, max_gen, wife )

def count_generations( tag, p ):
    if tag not in persons[p]:

       # do the count for the children
       for f in persons[p]['families']:
           for child in families[f]['children']:
               count_generations( tag, child )

       max_gen = 0
       # get the counts from the children
       for f in persons[p]['families']:
           for child in families[f]['children']:
               max_gen = max( max_gen, persons[child][tag] )

       persons[p][tag] = max_gen + 1

def show_counts( tag, p, person ):
    name  = ''
    birth = ''
    count = '?'
    if 'name' in person:
       name = person['name']
    if 'birth' in person:
       birth = person['birth']
    if tag in person:
       count = person[tag]

    print( count, p, name, birth )

def name_to_upper( name ):
   # person names are within slashes
   # might be "First /Last/"
   # or       "First /Last/ Title"

   parts = name.split( '/' )

   if len( parts ) > 1:
      parts[1] = parts[1].upper()

   return compact_spaces( ' '.join( parts ) )

def name_to_first( name ):
   # person names are within slashes
   # might be "First /Last/"
   # or       "First /Last/ Title"
   # or       "/Last/"

   parts = name.split( '/' )

   if parts[0]:
      # actually, take name up to the first space
      #return parts[0].strip().split()[0]
      # asiboro: change to use all names
      return parts[0].strip()
   else:
      return 'unknown'

def parent_name( which_parent, family ):
    name = 'unknown'
    if which_parent in family:
       person = family[which_parent]
       if 'name' in persons[person]:
          name = persons[person]['name']
    return name

def output_json( indent, comma, p ):
    # not bothering with json module, just output strings

    title = ''
    name = 'unknown'
    if 'name' in persons[p]:
       name = persons[p]['name']
    firstname = 'unknown'
    if 'title' in persons[p]:
       title = persons[p]['title']
    if 'first name' in persons[p]:
       firstname = persons[p]['first name']
    birth = None
    if 'birth' in persons[p]:
        birth = persons[p]['birth']
    death = None
    if 'death' in persons[p]:
        death = persons[p]['death']
    parents = None
    if 'child of' in persons[p]:
       child_of = persons[p]['child of']
       parents = parent_name( 'husband', families[child_of] )
       parents += ' and ' + parent_name( 'wife',  families[child_of] )

    value = str(p) + ' ' + name
    if birth:
       value += '\\nBorn: ' + birth
    if death:
       value += '\\nDied: ' + death
    if parents:
       value += '\\nParents: ' + parents

    n_children = 0
    for f in persons[p]['families']:
        n_children = n_children + len( families[f]['children'] )

    has_children = n_children > 0

    print( comma, end='' )
    print( indent + '{"name": "' + title + ' ' + firstname + '",', end='' )
    print( ' "detail": "' + value + '"', end='' )

    check = 'already output'
    persons[p][check] = True

    if has_children:
       print( ', "children": [' )
       comma = ''
       for f in persons[p]['families']:
           for child in families[f]['children']:
               if check in persons[child]:
                  print( 'Person', child, 'already output', file=sys.stderr )
               else:
                  output_json( indent + '  ', comma, child )
                  comma = ',\n'

       print( '' )
       print( indent + ']', end='' )
    else:
       print( ', "size": 1', end='' )

    print( '}', end='' )

def trace( indent, p ):
    name = 'unknown'
    if 'name' in persons[p]:
       name = persons[p]['name']
    parents = None
    if 'child of' in persons[p]:
       child_of = persons[p]['child of']
       parents = parent_name( 'husband', families[child_of] )
       parents += ' and ' + parent_name( 'wife',  families[child_of] )

    print( indent + str(p), name )
    #if parents:
    #   print( indent + parents )

    check = 'already output'
    persons[p][check] = True

    for f in persons[p]['families']:
        print( indent + 'family', f, parent_name( 'husband', families[f] ),'&',parent_name( 'wife',  families[f] ) )

        for child in families[f]['children']:
            if check in persons[child]:
               print( indent, ' !person already output' )
            trace( indent + '  ', child )

# these lists are globals

persons  = dict()
families = dict()

indi       = None
fam        = None
level1_key = ''

with open( datafile ) as inf:
   for line in inf:
       line = line.strip()
       if line:

          level = None
          key   = None
          value = None

          if len(line.split()) == 2:
             level, key = line.split( ' ' )
          else:
             level, key, value = line.split( ' ', 2 )
             value = escape_quote( compact_spaces( value ) )

          key = key.lower()

          if level == '0':
             level1_key = ''

             # starting a new item
             indi = None
             fam  = None

             if key.startswith( '@i' ):
                indi          = to_indi( key )
                if indi in persons:
                   print( 'Warning: person', indi, 'duplicated', file=sys.stderr )
                   indi = None
                else:
                   persons[indi] = dict()
                   persons[indi]['families'] = []

             elif key.startswith( '@f' ):
                fam           = to_fam( key )
                if fam in families:
                   print( 'Warning: family', fam, 'duplicated', file=sys.stderr )
                   fam = None
                else:
                   families[fam] = dict()
                   families[fam]['children'] = []

          elif level == '1':
             level1_key = key

             if key == 'name':
                if indi:
                   persons[indi]['name'] = name_to_upper( value )
                   persons[indi]['first name'] = name_to_first( value )

             elif key == 'famc':
                  if indi:
                     persons[indi]['child of'] = to_fam( value )

             elif key == 'fams':
                  if indi:
                     persons[indi]['families'].append( to_fam( value ) )

             elif key == 'sex':
                  if indi:
                     persons[indi]['sex'] = value.upper()

             elif key == 'chil':
                  if fam:
                     families[fam]['children'].append( to_indi( value ) )

             elif key == 'husb':
                  if fam:
                     families[fam]['husband'] = to_indi( value )

             elif key == 'wife':
                  if fam:
                     families[fam]['wife'] = to_indi( value )

          elif level == '2':
              if key == 'date':
                 if indi:
                    if level1_key == 'birt':
                       persons[indi]['birth'] = value
                    elif level1_key == 'deat':
                       persons[indi]['death'] = value

                 elif fam:
                    if level1_key == 'marr':
                       families[fam]['marriage'] = value

              elif key == 'plac':
                   if indi:
                      if level1_key == 'birt':
                         persons[indi]['birth place'] = value
                      elif level1_key == 'deat':
                         persons[indi]['death place'] = value
                   elif fam:
                      if level1_key == 'marr':
                         families[fam]['marriage place'] = value

              elif key == 'givn':
                   if indi and level1_key == 'name':
                      persons[indi]['given'] = value

              elif key == 'surn':
                   if indi and level1_key == 'name':
                      persons[indi]['surname'] = value

              elif key == 'npfx':
                   if indi and level1_key == 'name':
                      persons[indi]['title'] = value

if operation == 'list':
   for p in sorted( persons.keys() ):
       show_person( p, persons[p] )

elif operation == 'noparent':
   for p in sorted( persons.keys() ):
       if 'child of' not in persons[p]:
          show_person( p, persons[p] )

elif operation in ['json', 'sunburst']:
   p = check_selection()
   if p:
      print( 'var loadData =' )
      output_json( "", "", p )
      print( ';' )

elif operation == 'generation':
   tag = 'generations below'
   for p in persons:
       count_generations( tag, p )
   for p in persons:
       show_counts( tag, p, persons[p] )

elif operation == 'problem':
   for p in persons:
       find_problems( p )
   for f in families:
       find_fam_problems( f, families[f] )

elif operation == 'bloodmarriage':
   for p in persons:
       find_married_own_desc( p, 0, p )
   for f in families:
       find_married_cousins( f )

elif operation == 'trace':
   p = check_selection()
   if p:
      trace( "", p )

elif operation == 'ancestor':
   p = check_selection()
   if p:
      ancestors( "", 0, 1000000, p )

elif operation in ('grandparent', 'gparent'):
   p = check_selection()
   if p:
      ancestors( "", 0, 3, p )

elif operation in ('greatgrandparent', 'gparent'):
   p = check_selection()
   if p:
      ancestors( "", 0, 4, p )

else:
   print( 'Unknown operation', file=sys.stderr )
