# ================================================================================
# Project:   Kivy.Statechart - A Statechart Framework for Kivy
# Copyright: (c) 2010, 2011 Michael Cohen, and contributors.
# Python Port: Jeff Pittman, ported from SproutCore, SC.Statechart
# ================================================================================

from kivy_statechart.system.state import State

class StatechartSequenceMatcher:
    def __init__(self, statechartMonitor):
        self.statechartMonitor = statechartMonitor
        self.match = None
        self.MISMATCH = {}
  
    def begin(self):
        self._stack = []
        self.beginSequence()
        self._start = self._stack[0]
        return self
  
    def end(self):
        self.endSequence()
    
        if len(self._stack) > 0:
            raise "can not match sequence. sequence matcher has been left in an invalid state"
    
        monitor = self.statechartMonitor

        result = False
        
        if self._matchSequence(self._start, 0) == len(monitor.sequence):
            result = True

        self.match = result
    
        return result
  
    def entered(self, *arguments):
        self._addStatesToCurrentGroup('entered', arguments) # [PORT] js arguments, so *arguments added here
        return self
  
    def exited(self, *arguments):
        self._addStatesToCurrentGroup('exited', arguments)
        return self
  
    def beginConcurrent(self):
        group = { 'tokenType': 'concurrent', 'values': [] }

        if self._peek():
            self._peek()['values'].append(group)

        self._stack.append(group)

        return self
  
    def endConcurrent(self):
        self._stack.pop()
        return self
  
    def beginSequence(self):
        group = { 'tokenType': 'sequence', 'values': [] }

        if self._peek():
            self._peek()['values'].append(group)

        self._stack.append(group)
        return self
  
    def endSequence(self):
        self._stack.pop()
        return self
  
    def _peek(self):
        return None if len(self._stack) == 0 else self._stack[-1]
  
    def _addStatesToCurrentGroup(self, action, states):
        group = self._peek()

        for state in states:
            group['values'].append({ 'action': action, 'state': state })
  
    def _matchSequence(self, sequence, marker):
        values = sequence['values']
        monitor = self.statechartMonitor
        
        if not values:
            return marker

        if marker > len(monitor.sequence):
            return self.MISMATCH
        
        # values is hierarchical, so that it is: {values: [{ values: [{ values: ...
        # and actions are mixed in there.
        for val in values:
            if 'tokenType' in val:
                if val['tokenType'] == 'sequence':
                    marker = self._matchSequence(val, marker)
                elif val['tokenType'] == 'concurrent':
                    marker = self._matchConcurrent(val, marker)
            elif not self._matchItems(val, monitor.sequence[marker]):
                return self.MISMATCH
            else:
                marker += 1
      
            if marker == self.MISMATCH:
                return self.MISMATCH
    
        return marker

    # A
    # B (concurrent [X, Y])
    #   X
    #     M
    #     N
    #   Y
    #     O
    #     P
    # C
    # 
    # 0 1  2 3 4   5 6 7  8
    #      ^       ^
    # A B (X M N) (Y O P) C
    #      ^       ^
    # A B (Y O P) (X M N) C
  
    def _matchConcurrent(self, concurrent, marker):
        values = list(concurrent['values']) # copy
        tempMarker = marker
        match = False
        monitor = self.statechartMonitor
        
        if not values:
            return marker
    
        if marker > len(monitor.sequence):
            return self.MISMATCH
    
        # values is hierarchical, so that it is: {values: [{ values: [{ values: ... , tokenType: 'sequence'}
        # and actions are list items in values lists, with tokenType as the second key/value pair in the dicts.
        while len(values) > 0:
            for val in values:
                if 'tokenType' in val:
                    if val['tokenType'] == 'sequence':
                        tempMarker = self._matchSequence(val, marker)
                    elif val['tokenType'] == 'concurrent':
                        tempMarker = self._matchConcurrent(val, marker)
                elif not self._matchItems(val, monitor.sequence[marker]):
                    tempMarker = self.MISMATCH
                else:
                    tempMarker = marker + 1
      
                if tempMarker != self.MISMATCH:
                    break
      
            if tempMarker == self.MISMATCH:
                return self.MISMATCH

            values.remove(val)
              
            marker = tempMarker
    
        return marker
  
    def _matchItems(self, matcherItem, monitorItem):
        if matcherItem is None or monitorItem is None:
            return False
  
        if 'action' in matcherItem and matcherItem['action'] != monitorItem['action']:
            return False
    
        if 'state' in matcherItem and isinstance(matcherItem['state'], State) and matcherItem['state'] is monitorItem['state']:
            return True
    
        if 'state' in matcherItem and matcherItem['state'] == monitorItem['state'].name:
            return True
  
        return False
