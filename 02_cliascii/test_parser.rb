#!/usr/bin/env ruby

require_relative 'aa_streamer'

# Test the parser with a small sample
streamer = AsciiArtStreamer.new
streamer.load_art_database

puts "Successfully loaded art entries"
puts "First few entries:"

5.times do |i|
  if streamer.art_entries[i]
    entry = streamer.art_entries[i]
    puts "#{i+1}. #{entry[:title]} (#{entry[:dimensions]}) - #{entry[:art][0..20]}..."
  end
end