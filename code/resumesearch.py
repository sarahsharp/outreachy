#!/usr/bin/env python3
#
# Copyright 2017 Sarah Sharp <sharp@otter.technology>
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This script attempts to match skillset keywords in resumes with
# Outreachy projects. The skillset keyword lists are based on the
# Outreachy project list at:
# https://wiki.gnome.org/Outreachy/2017/MayAugust
#
# This program expects you to have created a directory with identically
# named PDF and text resume files. You can translate PDF files to text with:
# $ for i in `ls *.pdf`; do pdftotext $i; done

import argparse
import csv
import os
import re
import textwrap
#from fuzzywuzzy import fuzz
from enum import Enum
from collections import Counter
from shutil import copyfile

class outreachyProject:
    """Outreachy project name, description, keywords, and matching resume storage."""
    def __init__(self, name, short, description, keywords, printskip):
        self.name = name
        self.description = description
        self.keywords = keywords
        self.strongResumeMatches = []
        self.weakResumeMatches = []
        self.short = short
        self.printskip = printskip

class resumeFile:
    """Information relating to a text and pdf resume pair."""
    def __init__(self, path, textFileName, contents):
        self.path = path
        self.textFileName = textFileName
        self.pdfFileName = os.path.splitext(textFileName)[0] + '.pdf'
        self.contents = contents
        self.emails = re.findall(r'[\w\.-\_\+]+@[\w\.-]+', contents)
        self.strongProjectMatches = []
        self.weakProjectMatches = []

def readResumeFiles(directory):
    resumeFiles = []
    for f in [l for l in os.listdir(directory) if l.endswith('.txt') and
              not l.endswith('-email.txt') and
              not l.endswith('-email-tam.txt')]:
        with open(os.path.join(directory, f), 'r') as resume:
            contents = resume.read()
        resumeFiles.append(resumeFile(directory, f, contents))
    #print("Found", len(resumeFiles), "resume files")
    for r in resumeFiles:
        if len(r.emails) == 0:
            continue
        line = r.pdfFileName
        for email in r.emails:
            line = line + ' ' + email
        line = line + ' ' + str(len(r.contents))
    # The first email is usually the actual email.
    emails = [resume.emails[0] for resume in resumeFiles if resume.emails]
    edups = [item for item, count in Counter(emails).items() if count > 1]
    for email in edups:
        pdfs = [resume.pdfFileName for resume in resumeFiles if resume.emails and resume.emails[0] == email]
        print('Email duplicate:', email, ' '.join(pdfs))
    return resumeFiles

def searchForEmail(csvFile, resumeFiles):
    with open(csvFile, 'r') as csvFile:
        freader = csv.DictReader(csvFile, delimiter=',', quotechar='"')
        boothstops = []
        for row in freader:
            # Create a list of potential matches for the email we have.
            # Search through the list of emails in each PDF.
            # Use fuzzywuzzy to do a fuzzy search in case we misread an email.
            # No difference between pure match when I tried this, and going down to 80 only added false positives
            #m = [r for r in resumeFiles if len([email for email in r.emails if fuzz.ratio(row['Email'], email) > 90]) != 0]
            m = [r for r in resumeFiles if row['Email'] in r.emails]
            if len(m) == 0:
                continue
            files = set()
            for resume in m:
                files.add(resume.pdfFileName)
            boothstops.append((row['Email'], list(files)))
    return boothstops

projectsMay2017 = [
    #outreachyProject('Outreachy',
    #                 ['open source', 'free software', 'Linux', 'Unix', 'Solaris']),
    outreachyProject('Cadasta', 'a property rights tool',
                     'enhance user settings and create a user dashboard',
                     ['django'], []),
    outreachyProject('Cadasta', 'a property rights tool',
                     'add new login options',
                     ['django|oauth'], []),
    outreachyProject('Cadasta', 'a property rights tool',
                     'improve automated test coverage',
                     ['selenium'], []),

    outreachyProject('Ceph', 'a network filesystem',
                     'create a root cause analysis tool for Linux distributed systems',
                    ['linux', 'distributed systems'], ['linux', 'distributed systems']),
    outreachyProject('Ceph', 'a network filesystem',
                     'evaluate the performance of new reweight algorithms for balancing storage utilization',
                    ['statistics', 'storage', 'linux'], ['statistics', 'storage', 'linux']),
    outreachyProject('Ceph', 'a network filesystem',
                     'design a status dashboard to visualize Ceph cluster statistics',
                    ['python', 'linux', 'javascript', 'html5', 'css3'], []),
    outreachyProject('Ceph', 'a network filesystem',
                     'identify performance degradation in nodes and automate cluster response',
                    ['Linux', 'python', 'distributed systems'], []),
    outreachyProject('Ceph','a network filesystem',
                     'design a simplified database backend for the Ceph Object Gateway',
                    ['database', 'Linux', 'C\+\+'], ['database']),
    outreachyProject('Ceph','a network filesystem',
                     'port tests written in multiple languages to test the Amazon S3 storage protocol and Openstack Swift storage',
                    ['python', 'linux', 'storage'], ['storage']),

    outreachyProject('Debian', 'a Linux distribution',
                     'benchmark scientific packages for general and architecture specific builds',
                    ['linux', 'gcc'], ['linux']),
    outreachyProject('Debian', 'a Linux distribution',
                     'improve the Debian test database and website',
                    ['linux', 'python', 'sql', 'shell|bash|command-line'], ['linux', 'command-line']),
    outreachyProject('Debian', 'a Linux distribution',
                     'enhance the Debian test website',
                    ['html', 'css', 'linux', 'graphic'], ['linux', 'graphic']),
    outreachyProject('Debian', 'a Linux distribution',
                     'Add secure mail server support to FreedomBox (a web server for small machines)',
                    ['python', 'django', 'shell|bash|command-line'], ['command-line']),

    outreachyProject('Discourse', 'chat forum software',
                     'enhance their forum and chat web services',
                    ['rails', 'javascript|ember.js'], []),

    outreachyProject('Fedora', 'a Linux distribution',
                     'create a coloring book to explain technical concepts',
                     ['inkscape|scribus|storyboard|storyboarding|graphic design'], ['graphic design', 'storyboard', 'storyboarding']),
    outreachyProject('Fedora', 'a Linux distribution',
                     'improve Bodhi, the web-system that publishes updates for Fedora',
                     ['python', 'javascript|html|css|linux|fedora'], []),

    outreachyProject('GNOME', None,
                     'improve the recipes or maps applications',
                     ['gtk'], []),

    outreachyProject('Lagome', 'a microservices platform',
                     "create an online auction sample app to showcase Lagome's microservices",
                     ['java', 'scala|react|reactive'], ['react', 'reactive']),

    outreachyProject('Linux kernel', None,
                     'analyze memory resource release operators and fix Linux kernel memory bugs',
                     ['linux', 'operating systems', 'memory'], ['linux', 'operating systems', 'memory']),
    outreachyProject('Linux kernel', None,
                     'improve process ID allocation',
                     ['linux', 'operating systems', 'kernel'], ['linux', 'operating systems', 'kernel']),
    outreachyProject('Linux kernel', None,
                     'improve nftables (an in-kernel network filtration tool)',
                     ['linux', 'operating systems', 'networking'], ['linux', 'operating systems', 'networking']),
    outreachyProject('Linux kernel', None,
                     'write a driver for a sensor using the Industrial I/O interface',
                     ['linux', 'operating systems|robotics|embedded', 'C\+\+|C(?!\+\+)'],
                     ['linux', 'operating systems', 'robotics', 'embedded', 'c++']),
    outreachyProject('Linux kernel', None,
                     'improve documentation build system and translate docs into ReStructured Text format',
                     ['perl', 'python', 'operating systems'], ['operating systems']),

    outreachyProject('Mozilla', None,
                     None,
                     ['mozilla|firefox'], ['mozilla', 'firefox']),

    outreachyProject('OpenStack', 'software for cloud deployment and management',
                     'add continuous integration for OpenStack Identity Service (keystone) LDAP support',
                     ['python', 'shell|bash|command-line'], ['command-line']),

    outreachyProject('oVirt', 'virtualization management software',
                     'implement oVirt integration tests using Lago and the oVirt REST API',
                     ['python', 'rest'], ['rest']),
    outreachyProject('oVirt', 'virtualization management software',
                     'design an oVirt log analyzer for distributed systems',
                     ['python', 'linux', 'distributed systems'], ['distributed systems']),
    outreachyProject('oVirt', 'virtualization management software',
                     'rewrite oVirt UI dialogs in modern JavaScript technologies',
                     ['es6|react|redux'], []),

    outreachyProject('QEMU', 'hardware virtualization software',
                     'rework the QEMU audio backend',
                     ['C(?!\+\+)', 'audio'], ['audio']),
    outreachyProject('QEMU', 'hardware virtualization software',
                     'create a full and incremental disk backup tool',
                     ['C(?!\+\+)', 'python', 'storage'], ['storage']),
    outreachyProject('QEMU', 'hardware virtualization software',
                     "refactor the block layer's I/O throttling and write notifiers",
                     ['C(?!\+\+)', 'storage'], ['storage']),
    outreachyProject('QEMU', 'hardware virtualization software',
                     "code an emulated PCIe-to-PCI bridge",
                     ['pci|pcie'], ['pci', 'pcie']),
    outreachyProject('QEMU', 'hardware virtualization software',
                     "add x86 virtualization support on macOS using Hypervisor.framework",
                     ['C(?!\+\+)', 'mac', 'virtualization'], ['mac', 'virtualization']),
    outreachyProject('QEMU', 'hardware virtualization software',
                     "extend the current vhost-pci based inter-VM communication",
                     ['C(?!\+\+)', 'pci'], ['pci']),

    outreachyProject('Sugar Labs', 'a software-development and learning community',
                     'improve Music Blocks, an application for exploring fundamental musical concepts',
                     ['javascript|JS', 'music'], ['music']),

    outreachyProject('Wikimedia', 'a non-profit known for Wikipedia',
                     'write a Zotero translator and document the process',
                     ['javascript', 'documentation'], ['documentation']),
    outreachyProject('Wikimedia', 'a non-profit known for Wikipedia',
                     'improve and fix bugs in the quiz extension',
                     ['php', 'documentation'], ['documentation']),
    outreachyProject('Wikimedia', 'a non-profit known for Wikipedia',
                     'create user guides to help with translation outreach',
                     ['translation|localization'], ['translation', 'localization']),
    outreachyProject('Wikimedia', 'a non-profit known for Wikipedia',
                     'implement automatic edits on wikis connected to the Programs & Events Dashboard',
                     ['rails'], []),
    outreachyProject('Wikimedia', 'a non-profit known for Wikipedia',
                     'implement an automatic article feedback feature for the Programs & Events Dashboard',
                     ['rails'], []),

    outreachyProject('Wine', 'a tool to run Windows programs on Linux or BSD',
                     'implement a resource editor and dialog editor',
                     ['C(?!\+\+)', 'Windows', 'UI|UX'], ['windows', 'ui', 'ux']),
    outreachyProject('Wine', 'a tool to run Windows programs on Linux or BSD',
                     'implement missing D3DX9 APIs',
                     ['C(?!\+\+)', 'computer graphics'], []),
    outreachyProject('Wine','a tool to run Windows programs on Linux or BSD',
                     'implement Direct3D microbenchmarks',
                     ['C(?!\+\+)', 'opengl'], []),
    outreachyProject('Wine','a tool to run Windows programs on Linux or BSD',
                     'create automated game benchmarks',
                     ['C(?!\+\+)', 'game engine'], ['game engine']),
    outreachyProject('Wine','a tool to run Windows programs on Linux or BSD',
                     'port WineLib to a new architecture (such as PPC64, Sparc64, RISC-V, or x32)',
                     ['PPC|PowerPC|Sparc|Sparc64|RISC-V'], ['ppc', 'powerpc', 'sparc', 'sparc64', 'risc-v']),
    outreachyProject('Wine','a tool to run Windows programs on Linux or BSD',
                     'improve the AppDB website, which lists Wine support for Windows programs',
                     ['php', 'html', 'mysql'], []),

    outreachyProject('Xen Project', 'a virtualization platform',
                     'create golang bindings for libxl on the Xen hypervisor',
                     ['go', 'C(?!\+\+)'], []),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'create rust bindings for libxl on the Xen hypervisor',
                     ['rust'], ['rust']),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'enhance the KDD (Windows Debugger Stub) for the Xen hypervisor',
                     ['C(?!\+\+)', 'windows', 'kernel|debugger'], ['windows', 'debugger']),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'fuzz test the Xen hypercall interface',
                     ['C(?!\+\+)', 'assembly', 'gcc'], []),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'improve Mirage OS, a unikernel that runs on top of Xen',
                     ['ocaml'], []),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'create a Xen code review dashboard',
                     ['sql', 'javascript', 'html5', 'java'], []),
    #outreachyProject('Xen Project', 'a virtualization platform',
    #                 'implement tools for code standards checking using clang-format',
    #                 ['clang']),
    outreachyProject('Xen Project', 'a virtualization platform',
                     'add more FreeBSD testing to osstest',
                     ['freebsd|bsd|openbsd|netbsd|dragonfly'], ['freebsd', 'bsd', 'openbsd', 'netbsd', 'dragonfly']),

    outreachyProject('Yocto', 'a tool for creating embedded Linux distributions',
                     'improve and document the Yocto autobuilder',
                     ['C(?!\+\+)', 'python', 'distro|linux|yocto|openembedded', 'embedded|robotics|beaglebone|beagle bone|minnow|minnowboard|arduino'], ['distro', 'linux', 'yocto', 'embedded', 'robotics', 'beaglebone', 'beagle bone', 'minnow', 'minnowboard', 'arduino']),
]

# We have two types of resumes:
# 1. They matched *some* but not all of the important keywords for a project.
# 2. They matches all of the keywords we need.
def matchResumes(resumeFiles):
    for resume in resumeFiles:
        for project in projectsMay2017:
            matches = [set(re.findall(r'\b(?:' + keyword + r')\b', resume.contents, flags=re.IGNORECASE)) for keyword in project.keywords]
            # New syntax for me!
            # * takes a list and expands it to arguments to a function.
            # ** takes a dictionary and expands it to key-value arguments to a function.
            # union combines the list of sets and removes duplicates.
            keywords = set.union(*matches)
            if all(matches):
                resume.strongProjectMatches.append((project, keywords))
                project.strongResumeMatches.append(resume)
            elif any(matches):
                resume.weakProjectMatches.append((project, keywords))
                project.weakResumeMatches.append(resume)

def matchWithProjects(resumeFiles):
    goldresumes = []
    matchResumes(resumeFiles)


    #for project in projectsMay2017:
    #    print(len(project.strongResumeMatches), '\t', project.name, '\t', project.description)

    #print('Resumes to review:', len([resume for resume in resumeFiles if len(resume.strongProjectMatches) > 0]))

    #print('Resumes with strong matches:')
    #for i in range(1, 9):
    #    resumeCount = [resume for resume in resumeFiles if len(resume.strongProjectMatches) == i]
    #    if resumeCount:
    #        print(len(resumeCount), 'with', i, 'strong matches')

    #resumeCount = [resume for resume in resumeFiles if len(resume.strongProjectMatches) > 9]
    #if resumeCount:
    #    print(len(resumeCount), 'with > 10 matches')

    #print('Resumes with weak matches:')
    #for i in range(1, 9):
    #    resumeCount = [resume for resume in resumeFiles
    #                   if not resume.strongProjectMatches and len(resume.weakProjectMatches) == i]
    #    if resumeCount:
    #        print(len(resumeCount), 'with', i, 'weak matches')

    #resumeCount = [resume for resume in resumeFiles
    #               if not resume.strongProjectMatches and len(resume.weakProjectMatches) > 9]
    #if resumeCount:
    #    print(len(resumeCount), 'with > 10 matches')

header1 = '''From: Sarah Sharp <saharabeara@gmail.com>
'''
header3 = '''Reply-to: outreachy-admins@gnome.org
Subject: Internship opportunities

'''

noBooth = '''Greetings!

I'm Sarah Sharp, and we both attended the Tapia conference last
September. I'd like to invite you to apply to two programs programs
that provide paid internships in open source. Interns will work
remotely with experienced mentors.

'''

# offer to host Outreachy session if they signed up at the booth or mention open
# source in their resume?
# What about the students at universities hosting introductory sessions?
atBooth = '''Greetings!

I'm Sarah Sharp, and we met when you stopped by the Outreachy booth
at the Tapia conference last September. I'd like to invite you to
apply to two programs programs that provide paid internships.
Interns will work remotely with experienced mentors.

'''

generalInfo = '''Google Summer of Code is open to all university students:

https://developers.google.com/open-source/gsoc/

Outreachy is open internationally to women (both cis & trans),
trans men, and genderqueer folks. It is also open to U.S. residents
and nationals of any gender who are Black/African American,
Hispanic/Latin@, American Indian, Alaska Native, Native Hawaiian, or
Pacific Islander.

https://wiki.gnome.org/Outreachy/

Both programs offer internships from May 30 to August 30.

Google Summer of Code application process runs from Feb 28 to Apr 3,
while Outreachy's application process runs from Feb 16 to Mar 30.
Google Summer of Code application only requires a project proposal.
Outreachy also requires applicants to make project contributions.

'''

moreInfo = '''The full list of Outreachy internship projects is available at:

https://wiki.gnome.org/Outreachy/2017/MayAugust

Please let me know if you have any questions about the Outreachy
program. Outreachy coordinators (Marina, Karen, Cindy, Tony, and I)
can all be reached at outreachy-admins@gnome.org You can contact all
organization mentors by emailing outreachy-list@gnome.org

I hope you'll apply!

Thanks,
Sarah Sharp
'''

# TODO:
# 1. Remove the generic description when we have a good resume match; it's more personal.

LINEWRAP = 68

def writeInitialInvitation(emaildir, resume, boothlist, matches):
    project, keywords = matches[0]
    para = ("Based on your resume, if you're eligible for Outreachy, it looks like you might be a good fit for in an internship with " +
                      project.name)
    if project.short:
        para = para +' (' + project.short + ')'
    if not project.description:
        return textwrap.fill(para + '.', LINEWRAP, replace_whitespace=False) + '\n\n'

    para = para + ' which is offering an internship to ' + project.description
    keywords = [k for k in keywords if k.lower() not in project.printskip]
    if keywords:
        para = para + ' that involves working with '
        k = list(set(keywords))
        if len(k) == 1:
            para = para + k[0]
        elif len(k) == 2:
            para = para + ' and '.join(k)
        else:
            para = para + ', '.join(k[:-1]) + ' and ' + k[-1]
    return para

def writeStrongInvitation(emaildir, resume, boothlist):
    matches = sorted(resume.strongProjectMatches, key=lambda match: len(match[1]))
    project, keywords = matches[0]
    para = writeInitialInvitation(emaildir, resume, boothlist, matches)

    if len(resume.strongProjectMatches) > 1:
        para = (para + '. You may also be interested in the ' +
                          project.name + ' internship')
        if len(resume.strongProjectMatches) > 2:
            para = para + 's to '
        else:
            para = para + ' to '
        descriptions = []
        for project, keywords in matches[1:-1]:
            para = para + project.description + ' or the internship to '
        para = para + matches[-1][0].description

    return textwrap.fill(para + '.', LINEWRAP) + '\n\n'

def writeMultipleStrongInvitation(emaildir, resume, boothlist):
    matches = sorted(resume.strongProjectMatches, key=lambda match: len(match[1]))
    project, keywords = matches[0]
    para = writeInitialInvitation(emaildir, resume, boothlist, matches)

    doneProjects = set()
    for project, keywords in matches[1:]:
        projmatches = [(p, k) for p, k in matches[1:]
                       if p not in doneProjects and
                       p.name == project.name
                      ]
        if not projmatches:
            continue
        doneProjects.add(project)
        for p, k in projmatches:
            para = (para + '. You may also be interested in the ' +
                              p.name + ' internship')
            if not p.description:
                break
            if len(projmatches) > 2:
                para = para + 's to '
            else:
                para = para + ' to '
            descriptions = []
            for p2, k2 in projmatches[1:-1]:
                para = para + p2.description + ' or the internship to '
            para = para + projmatches[-1][0].description
    return textwrap.fill(para + '.', LINEWRAP) + '\n\n'

class emailType(Enum):
    strong = 1
    mixed = 2
    weak = 3

def craftEmail(emaildir, resume, boothlist, strength):
    email = header1 + 'To: ' + ', '.join(resume.emails) + '\n' + header3
    if resume.pdfFileName in boothlist:
        email = email + atBooth
    else:
        email = email + noBooth
    if strength is emailType.strong:
        email = (email + generalInfo +
                 writeStrongInvitation(emaildir, resume, boothlist) +
                 moreInfo)
    elif strength is emailType.mixed:
        email = (email + generalInfo +
                 writeMultipleStrongInvitation(emaildir, resume, boothlist) +
                 moreInfo)
    ext = '-email.txt'

    with open(os.path.join(emaildir, os.path.splitext(resume.textFileName)[0] + ext), 'w') as f:
        f.write(email)

def createFormEmails(directory, resumeFiles, boothlist):
    # For all resumes with one strong match or multiple strong matches with the same organization:
    # Create a directory with the organization name (lowercase, with spaces replaced with dashes)
    # Copy pdf resume into that directory, create basename-email.txt
    oneStrong = [resume for resume in resumeFiles if len(resume.strongProjectMatches) == 1]
    print('Resumes with exactly one match:', len(oneStrong))
    left = [resume for resume in resumeFiles if resume not in oneStrong]
    for resume in left:
        if not resume.strongProjectMatches:
            continue
        firstMatch = resume.strongProjectMatches[0][0].name
        for match in resume.strongProjectMatches[1:]:
            if match[0].name != firstMatch:
                firstMatch = ''
                break
        if firstMatch:
            oneStrong.append(resume)
    left = [resume for resume in resumeFiles if resume not in oneStrong]
    print('Resumes with exactly one match or multiple matches with same org:', len(oneStrong))
    print('Other resumes:', len(left))

    for project in projectsMay2017:
        matches = [resume for resume in oneStrong if resume.strongProjectMatches[0][0].name == project.name]
        if not matches:
            continue
        dirpath = os.path.join(directory, 'emails-' + re.sub(r'\s+', '-', project.name.lower()))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        for resume in matches:
            try:
                if not os.path.exists(os.path.join(dirpath, resume.pdfFileName)):
                    copyfile(os.path.join(directory, resume.pdfFileName),
                             os.path.join(dirpath, resume.pdfFileName))
            except:
                print('Could not find pdf file for', resume.textFileName)
                continue
            craftEmail(dirpath, resume, boothlist, emailType.strong)

    # For all resumes with strong matches with multiple orgs (but less than 4 orgs):
    # Create a directory called strong-mixed.
    # Copy pdf resume into that directory, create basename-email.txt
    #
    # "Based on your resume, it looks like you might be interested in an
    # internship with $PROJECT that involves $KEYWORDS which is offering an internship for
    # $DESCRIPTION.
    #
    # Additionally, you might be interested in $PROJECT that involves $KEYWORDS which 
    # is offering an internship for $DESCRIPTION."
    mixed = [resume for resume in resumeFiles if resume not in oneStrong and resume.strongProjectMatches]
    dirpath = os.path.join(directory, 'mixed')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    for resume in mixed:
        try:
            if not os.path.exists(os.path.join(dirpath, resume.pdfFileName)):
                copyfile(os.path.join(directory, resume.pdfFileName),
                         os.path.join(dirpath, resume.pdfFileName))
        except:
            print('Could not find pdf file for', resume.textFileName)
            continue
        craftEmail(dirpath, resume, boothlist, emailType.mixed)

    # For all resumes with strong matches with 4 or more orgs:
    # Create a directory called strong-scattered.
    # Copy pdf resume into that directory, create basename-email.txt

    # For all weakly matched resumes - figure out top keywords that matched weak resumes.
    hitcount = Counter()
    for resume in [resume for resume in resumeFiles if not resume.strongProjectMatches]:
        allkeywords = set()
        for project, keywords in resume.weakProjectMatches:
            allkeywords.update(keywords)
            for keyword in keywords:
                allkeywords.add(keyword)
        hitcount.update(allkeywords)

    # Take the top N keywords that weakly matched, find all projects that matched those keywords.
    # "Based on your resume, it looks like you might be interested in Outreachy
    # projects involving $KEYWORD like $MATCHES"

def craftGenericEmail(emaildir, resume):
    if not resume.emails:
        address = ''
    else:
        address = resume.emails[0]
    email = header1 + 'To: ' + address + '\n' + header3
    email = email + noBooth
    email = (email + generalInfo + moreInfo)
    ext = '-email.txt'

    with open(os.path.join(emaildir, os.path.splitext(resume.textFileName)[0] + ext), 'w') as f:
        f.write(email)

def main():
    parser = argparse.ArgumentParser(description='Search text resume files for skillset matches.')
    parser.add_argument('dir', help='Directory with .txt resume files')
    parser.add_argument('--csv', help='CSV file with name <email>,matching resume file of people who stopped by the booth')
    parser.add_argument('--notus', help='Directory with .txt resumes files that may be non-U.S. residents')
    parser.add_argument('--done', help='Directory with .txt resume files that have been contacted')
    parser.add_argument('--generic', help='Simply create generic emails and ignore project matches', default=False)
    #parser.add_argument('matches', help='file to write potential matches to')
    args = parser.parse_args()
    resumeFiles = readResumeFiles(args.dir)

    # Check to see if we have resumes to process that we've already
    # send email to.
    if args.done:
        doneResumes = readResumeFiles(args.done)
        emails = [resume.emails[0] for resume in doneResumes if resume.emails]
        for email in emails:
            pdfs = [resume.pdfFileName for resume in resumeFiles if resume.emails and resume.emails[0] == email]
            matches = [resume.pdfFileName for resume in doneResumes if resume.emails and resume.emails[0] == email]
            if pdfs:
                print('Already contacted:', email, ' '.join(pdfs), 'matches done resume', ' '.join(matches))
    if args.notus:
        notusResumes = readResumeFiles(args.notus)

    if args.generic:
        genericdir = os.path.join(args.dir, 'generic-todo')
        if not os.path.exists(genericdir):
            os.makedirs(genericdir)
        for resume in resumeFiles:
            craftGenericEmail(genericdir, resume)
        return

    boothstops = (searchForEmail(args.csv, resumeFiles) +
                  searchForEmail(args.csv, doneResumes) +
                  searchForEmail(args.csv, notusResumes))
    boothlist = set()
    for email, filelist in boothstops:
        boothlist.update(filelist)
    print('Booth stop list', boothstops)
    print('Booth stop pdfs', boothlist)
    print('Done resumes', [resume.pdfFileName for resume in doneResumes])

    matchWithProjects(resumeFiles)
    boothandresume = len([resume for resume in resumeFiles
               if resume.pdfFileName in boothlist
               and len(resume.strongProjectMatches)])
    print('People who stopped by the booth who have a resume and need an email:', boothandresume)
    print('People who stopped by the booth who have a resume and have been sent email:',
          len([resume for resume in doneResumes
               if resume.pdfFileName in boothlist]))
    print('People who stopped by the booth who have a resume and may be non-U.S. citizens:',
          len([resume for resume in notusResumes
               if resume.pdfFileName in boothlist]))
    createFormEmails(args.dir, resumeFiles, boothlist, generic)

if __name__ == "__main__":
    main()
