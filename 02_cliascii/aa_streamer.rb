#!/usr/bin/env ruby

require 'optparse'

class AsciiArtStreamer
  attr_reader :art_entries
  
  def initialize(database_file = 'asciiartdb-asciiarteu.txt')
    @database_file = database_file
    @art_entries = []
    @interval = 2
  end

  def parse_options
    OptionParser.new do |opts|
      opts.banner = "Usage: #{$0} [options]"
      
      opts.on('-i', '--interval SECONDS', Float, 'Display interval in seconds (default: 2)') do |seconds|
        @interval = seconds
      end
      
      opts.on('-h', '--help', 'Show this help message') do
        puts opts
        exit
      end
    end.parse!
  end

  def load_art_database
    unless File.exist?(@database_file)
      puts "Error: Database file '#{@database_file}' not found!"
      exit 1
    end

    puts "Loading ASCII art database..."
    
    current_entry = {}
    state = :title
    
    File.foreach(@database_file) do |line|
      line = line.chomp
      
      case state
      when :title
        if !line.empty?
          current_entry[:title] = line
          state = :dimensions
        end
      when :dimensions
        if line.match(/^\d+x\d+$/)
          current_entry[:dimensions] = line
          state = :category
        end
      when :category
        if !line.empty?
          current_entry[:category] = line
          state = :art
        end
      when :art
        if !line.empty?
          current_entry[:art] = line
          @art_entries << current_entry.dup
          current_entry.clear
          state = :title
        end
      end
    end
    
    puts "Loaded #{@art_entries.length} ASCII art entries"
  end

  def clear_screen
    system('clear') || system('cls')
  end

  def display_art(entry)
    clear_screen
    puts "=" * 50
    puts "Title: #{entry[:title]}"
    puts "Size: #{entry[:dimensions]}"
    puts "=" * 50
    puts
    puts entry[:art]
    puts
    puts "Press Ctrl+C to stop"
  end

  def stream
    if @art_entries.empty?
      puts "No ASCII art entries found!"
      return
    end

    puts "Starting ASCII art stream (#{@interval}s intervals)..."
    puts "Press Ctrl+C to stop"
    sleep 2

    trap('INT') do
      puts "\n\nStopping ASCII art stream. Goodbye!"
      exit 0
    end

    loop do
      entry = @art_entries.sample
      display_art(entry)
      sleep @interval
    end
  end

  def run
    parse_options
    load_art_database
    stream
  end
end

if __FILE__ == $0
  streamer = AsciiArtStreamer.new
  streamer.run
end