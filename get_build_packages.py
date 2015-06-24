#!/usr/bin/env python
"""Get package version"""


import apt
import apt_pkg
import argparse
import os
import re
import sys

from shutil import copyfile

class TrustyPackages:

    """Package processing
    """
    def __init__(self):
        """Docstring"""
        self.package_dic = {}

    def prepare_apt(self, version, sources_list_file, cache_path='cache'):
        try:
            current_dir = os.getcwd()
        except:
            current_dir = './'

        path_to_sources_list_file = os.path.join(current_dir, sources_list_file)
        path_to_cache = os.path.join(current_dir, cache_path, version)

        cache = apt.cache.Cache(rootdir=path_to_cache)
        path_to_sources_list = os.path.join(path_to_cache, 'etc/apt/sources.list')

        copyfile(path_to_sources_list_file, path_to_sources_list)

        cache.clear()
        cache.update()
        cache.open()

        if len(cache) == 0:
            print('Cache is still empty after update. Check sources list. Retrying.')
            cache = self.prepare_apt(version, sources_list_file)

        return cache

def main(args):
    packages = TrustyPackages()
    if args.fuel_version:
        repo_cache = packages.prepare_apt(args.fuel_version, args.sources_list_file)

    if not args.fuel_version:
        print('Please specify Fuel version with -f option.')

    if args.python_modules_file and os.path.exists(args.python_modules_file):
        with open(args.python_modules_file, 'r') as python_modules_lines:
            for line in python_modules_lines:
                package_from_file = re.sub('\s+', '', line)
                for package in repo_cache.keys():
                    if package == package_from_file:
                        cur_pkg = repo_cache[package]
                        highest_version = '0'
                        for pkg_version in cur_pkg.versions:
                            comparison_result = apt_pkg.version_compare(pkg_version.version, highest_version)
                            if (comparison_result >= 0):
                                highest_version = pkg_version.version

                        print("{package} ==> {version}".format(package=package, version=highest_version))
                        break
    else:
        print('Please specify path to python modules list.')

    if repo_cache:
        repo_cache.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get package version.')
    parser.add_argument('-p', '--python-modules-file', metavar=('PMOD'), type=str,
                        help='Path to python modules list', default='python-modules.txt')
    parser.add_argument('-s', '--sources-list-file', metavar=('SRCL'), type=str,
                        help='Path to sources list (Ubuntu repos)')
    parser.add_argument('-f', '--fuel-version', metavar=('FVER'), type=str,
                        help='Fuel version', default='7.0')
    parser.add_argument('-i', '--info', action='version',
                        version='Version: 1.0')
    args = parser.parse_args()

    main(args)