#!/usr/bin/env python3
"""Apply complete-classic regressions to the Republic edition."""
import unittest
import test_classic_full_editions as common
class RepublicFullEditions(common.ClassicFullEditions):
 series='sae-republic'
 source_units=707
 has_edition_notice=False
 english_checks={
  'ep01':('the same cut','contingent initiative','in precisely the opposite direction','harder story than getting out'),
  'ep02':('not an eternal IOU','Exemption here is no honor','not its output'),
  'ep03':('Nor are they claimed to be exhaustive or mutually exclusive','the ranking would not disappear','original ledger'),
  'ep04':('a bill, not a command','not the number of bad acts but the threshold','no creditor, no due date'),
  'ep05':('sixteen levels','not been canceled or suppressed','becoming one out of many')}
if __name__=='__main__':unittest.main()
