#! /usr/bin/env python

# Copyright (C) 2007 Eddy Pronk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import glob
import string
import lineage
from optparse import OptionParser

def chdir(dir):
    #print 'chdir %s' % dir
    os.chdir(dir)

class Scanner:
    def __init__(self, directory_visitor = None):
        self.directory_visitor = directory_visitor

    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))

        return newlist

    def scan(self, dir):
        self.scan_root = dir
        self.traverse(dir)
    
    def traverse(self, dir, parent = None):
        cwd = os.getcwd()
        chdir(dir)
        self.directory_visitor.on_enter_dir(dir, cwd)
        list = glob.glob("*")
        for l in list:
            if os.path.isdir(l):
                self.traverse(l, os.getcwd())
            else:
                #self.directory_visitor.on_file(os.getcwd()[len(self.scan_root) + 1:], l)
                self.directory_visitor.on_file(os.getcwd(), l)

        self.directory_visitor.on_leaving_dir(os.getcwd(), cwd)
        chdir(cwd)

class FlayGuy:
    def on_dir(self, dir):
        print 'entering %s' % dir
    def on_leaving_dir(self, file):
        print 'leaving %s' % file
    def on_file(self, file):
        print 'file %s' % file

class Context:
    def __init__(self):
        self.media_files = []
        self.meta_data_files = []
        self.album_root = None
        self.is_multi_disc = False

class ScanGuy:

    def make_lineage(self):
        l = lineage.Lineage(options)
        l.on_cue_sheet_written = self.callback
        return l

    def __init__(self, callback = None):
        self.media_types = set( ['.ape', '.flac'] )
        self.meta_data_types = set( ['.txt'] )
        self.callback = callback
        self.lineage = self.make_lineage()
        self.context = Context()
        self.disc_number = 1
        self.parent_done = False # metadata in parent has not been read

    def on_enter_dir(self, dir, parent = None):
        print 'entering %s' % dir

        res = re.search('(CD|cd|Disc)\s*([0-9])', dir)
        if res is not None:
            self.is_multi_disc = True

    def on_leaving_dir(self, dir, parent = None):
        print 'before leaving %s (parent %s)' % (dir, parent)
        if self.context.album_root == None:
            if self.is_multi_disc:
                print 'multi disc set'
                album_root = parent
            else:
                print 'single disc'
                album_root = dir

            if len(self.context.media_files):
                print 'content found in %s' % dir
                print 'setting album_root to %s' % album_root
                self.context.album_root = album_root

        if dir == self.context.album_root:
            print 'album done'

            def relative_path(path1, path2):
                return path1[len(path2) + 1:]

            cwd = os.getcwd()

            print 'content:'
            for item in self.context.media_files:
                print "'%s' '%s'" % (relative_path(item[0], cwd), item[1])

            print 'meta data:'
            for item in self.context.meta_data_files:
                filename = os.path.join(relative_path(item[0], cwd), item[1])
                self.lineage.parse(filename)

            self.lineage.write_cue_sheets()
            self.lineage = self.make_lineage()
            self.context = Context()

        print 'leaving %s' % dir

    def on_leaving_dir_old(self, dir, parent = None):
        if len(self.media_files):
            content_dir = os.getcwd()
            self.lineage.album.disc(self.disc_number).content_root = content_dir
            txt = self.glob(content_dir, '\.(txt|ffp|md5)$')
            if len(txt):
                print 'searching for meta data -- found!'
            else:
                print 'searching for meta data -- not found, trying parent dir'

            content = glob.glob("*.flac") 

            if not self.parent_done:
                chdir(parent)
                extra_txt = self.glob(parent, '\.(txt|ffp|md5)$')

                if len(extra_txt):
                    print 'searching for meta data in parent because we have a multi disc set -- found!'
                    album_dir = os.getcwd()
                    txt.extend(extra_txt)
                else:
                    print 'searching for meta data -- not found!'
                    album_dir = dir
                self.parent_done = True

                if len(txt):
                    self.album_dir = album_dir
                    content_root = os.getcwd()

                class FileFaker:
                    def write(self, string):
                        pass

                #self.lineage.parse(txt, content)

            else:
                print 'already have info from parent'

        print 'leaving %s' % dir

        if dir == self.album_dir:
            print 'write_cue_sheet in %s' % os.getcwd()
            self.lineage.write_cue_sheets()
            self.lineage = self.make_lineage()
            self.album_dir = ''
            self.parent_done = False
            for item in self.media_files:
                print item
                pass

    def on_file(self, dir, file):
        #print "on_file dir='%s' file='%s'" % (dir, file)
        (root, ext) = os.path.splitext(file)
        if ext in self.media_types:
            self.context.media_files.append( [dir, file] )
        elif ext in self.meta_data_types:
            self.context.meta_data_files.append( [dir, file] )

        expr = '\.(flac|ape|shn)$'
        res = re.search(expr, file)
        if res is not None and os.path.isfile(file):
            pass
            #self.media_files.append(file)
            #os.system('rm %s' % file)

    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))
        return newlist

class RegressionTester:
    def __init__(self):
        self.tests = 0
        self.failed = 0
        
    def compare(self, file):
        self.tests += 1
        expected_file = file + '.expected'
        #os.system('cp "%s" "%s"' % (file, expected_file))
        cmd = 'diff "%s" "%s"' % (expected_file, file)
        print cmd
        res = os.system(cmd)
        if(res != 0):
            self.failed += 1
        else:
            os.remove(file)

    def report(self):
        print 'ran %i tests, failed %i' % (self.tests, self.failed)
        

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option("-R", "--regression-testing", dest="regression_testing", action="store_true",
                      help="runs regression tests")
    parser.add_option("-f", "--force", dest="overwrite", action="store_true",
                      help="Forces overwriting of cue files.")

    (options, args) = parser.parse_args()

    if options.regression_testing:
        options.overwrite = True
        tester = RegressionTester()
        f = ScanGuy(callback=tester.compare)
        args = [ '/home/epronk/src/transcode-testing' ]
    else:
        f = ScanGuy()

    s = Scanner(f)

    for path in args:
        print 'scanning %s' % path
        s.scan(path)

    if options.regression_testing:
        tester.report()
