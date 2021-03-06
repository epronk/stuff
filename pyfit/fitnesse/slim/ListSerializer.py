'''
package fitnesse.slim;

import java.util.List;

import fitnesse.util.ListUtility;
'''

'''
 Packs up a list into a serialized string using a special format.  The list items must be strings, or lists.
 They will be recursively serialized.
 
 Format:  [iiiiii:llllll:item...]
 All lists (including lists within lists) begin with [ and end with ].  After the [ is the 6 digit number of items
 in the list followed by a :.  Then comes each item which is composed of a 6 digit length a : and then the value
 of the item followed by a :.  
'''

def serialize(data):
    return ListSerializer(data).serialize()

class ListSerializer(object):
    def __init__(self, data):
        self.data = data
        self.result = ''


        '''
  private StringBuffer result;
  private List<Object> list;

  public ListSerializer(List<Object> list) {
    this.list = list;
    result = new StringBuffer();
  }

  public static String serialize(List<Object> list) {
    return new ListSerializer(list).serialize();
  }
'''
    def serialize(self):
        self.result += '['
        self.appendLength(len(self.data))
        for o in self.data:
            s = self.marshalObjectToString(o)
            self.appendLength(len(s))
            self.appendString(s)
        self.result += ']'
        return self.result
    '''
  public String serialize() {
    result.append('[');
    appendLength(list.size());

    for (Object o : list) {
      String s = marshalObjectToString(o);
      appendLength(s.length());
      appendString(s);
    }
    result.append(']');
    return result.toString();
  }

  private String marshalObjectToString(Object o) {
    String s;
    if (o == null)
      s = "null";
    else if (o instanceof String)
      s = (String) o;
    else if (o instanceof List)
      s = ListSerializer.serialize(ListUtility.uncheckedCast(Object.class, o));
    else
      s = o.toString();
    return s;
  }
  '''
    def marshalObjectToString(self, o):
        s = ''
        if o == None:
            s = 'null'
        elif type(o) == str:
            s = o
        elif type(o) == list:
            s = serialize(o)
        return s
    '''

  private void appendString(String s) {
    result.append(s).append(':');
  }
  '''
    def appendString(self, s):
        self.result += s + ':'

    '''

  private void appendLength(int size) {
    result.append(String.format("%06d:", size));
  }
'''
    def appendLength(self, size):
        self.result += "%06d:" % size

'''
}
'''
