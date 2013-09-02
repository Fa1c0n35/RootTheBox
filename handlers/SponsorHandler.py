# -*- coding: utf-8 -*-
'''
Created on Sept 9, 2013

@author: lavalamp

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import logging

from handlers.BaseHandlers import BaseHandler

class SponsorHandler(BaseHandler):
    
    def get(self, *args, **kwargs):
        ''' Renders the sponsors page '''
        self.render("public/sponsors.html")