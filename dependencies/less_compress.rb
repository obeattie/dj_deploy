#!/usr/bin/env ruby

# Passes the css passed-in through stdin through the less preprocessor, and returns
# the compressed result as the stdout. This may well be the most ghetto-fabulous
# Ruby script ever compiled.

require 'rubygems'
require 'less'

puts Less::Engine.new(File.new(ARGV[0])).to_css
