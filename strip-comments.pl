#!/usr/bin/perl

while (<STDIN>) { 
  s/(?<!\\)\%.*$/\%/;
  #print if not /^\s*\%\s*$/; 
  print
}

exit(0);
