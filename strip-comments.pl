#!/usr/bin/perl

# strips latex comments for paper submission

while (<STDIN>) { 
  if (s/(?<!\\)\%.*$//) {
    print if (not /^$/);
  }
  else {
    print; 
  }
}

exit(0);
