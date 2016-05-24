import {noop} from '../core/utils';


export const linkTemplate = `<a ng-href="{{link.href}}" title="{{link.title}}" ng-click="links.click($event, link)"
ng-attr-target="{{link.target}}" ng-class="link.klass" bs-tooltip="tooltip">
<span ng-if="link.left" class="left-divider"></span>
<i ng-if="link.icon" class="{{link.icon}}"></i>
<span>{{link.label || link.name}}</span>
<span ng-if="link.right" class="right-divider"></span></a>`;


export const navbarTemplate = `<nav ng-attr-id="{{navbar.id}}" class="navbar navbar-{{navbar.theme}}"
ng-class="{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}"
ng-style="navbar.style" role="navigation">
    <div ng-class="navbar.container">
        <div class="navbar-header">
            <button ng-if="navbar.toggle" type="button" class="navbar-toggle" ng-click="navbar.isCollapsed = !navbar.isCollapsed">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <ul ng-if="navbar.itemsLeft" class="nav navbar-nav navbar-left">
                <li ng-repeat="link in navbar.itemsLeft" ng-class="{active:links.activeLink(link)}" lux-link></li>
            </ul>
            <a ng-if="navbar.brandImage" href="{{navbar.url}}" class="navbar-brand" target="{{navbar.target}}">
                <img ng-src="{{navbar.brandImage}}" alt="{{navbar.brand || 'brand'}}">
            </a>
            <a ng-if="!navbar.brandImage && navbar.brand" href="{{navbar.url}}" class="navbar-brand" target="{{navbar.target}}">
                {{navbar.brand}}
            </a>
        </div>
        <nav class="navbar-collapse"
             uib-collapse="navbar.isCollapsed"
             expanding="navbar.expanding()"
             expanded="navbar.expanded()"
             collapsing="navbar.collapsing()"
             collapsed="navbar.collapsed()">
            <ul ng-if="navbar.items" class="nav navbar-nav navbar-left">
                <li ng-repeat="link in navbar.items" ng-class="{active:links.activeLink(link)}" lux-link></li>
            </ul>
            <ul ng-if="navbar.itemsRight" class="nav navbar-nav navbar-right">
                <li ng-repeat="link in navbar.itemsRight" ng-class="{active:links.activeLink(link)}" lux-link></li>
            </ul>
        </nav>
    </div>
</nav>`;

export const sidebarTemplate = `<lux-navbar class="sidebar-navbar" ng-class="{'sidebar-open-left': navbar.left, 'sidebar-open-right': navbar.right}"></lux-navbar>
<aside ng-repeat="sidebar in sidebars"
       class="sidebar sidebar-{{ sidebar.position }}"
       ng-attr-id="{{ sidebar.id }}"
       ng-class="{'sidebar-fixed': sidebar.fixed, 'sidebar-open': sidebar.open, 'sidebar-close': sidebar.closed}" bs-collapse>
    <div class="nav-panel">
        <div ng-if="sidebar.user">
            <div ng-if="sidebar.user.avatar_url" class="pull-{{ sidebar.position }} image">
                <img ng-src="{{sidebar.user.avatar_url}}" alt="User Image" />
            </div>
            <div class="pull-left info">
                <p>{{ sidebar.infoText }}</p>
                <a ng-attr-href="{{sidebar.user.username ? '/' + sidebar.user.username : '#'}}">{{sidebar.user.name}}</a>
            </div>
        </div>
    </div>
    <ul class="sidebar-menu">
        <li ng-if="section.name" ng-repeat-start="section in sidebar.sections" class="header">
            {{section.name}}
        </li>
        <li ng-repeat-end ng-repeat="link in section.items" class="treeview"
        ng-class="{active:links.activeLink(link)}" ng-include="'subnav'"></li>
    </ul>
</aside>
<div class="sidebar-page" ng-class="{'sidebar-open-left': navbar.left, 'sidebar-open-right': navbar.right}" ng-click="closeSidebars()">
    <div class="overlay"></div>
</div>

<script type="text/ng-template" id="subnav">
    <a ng-href="{{link.href}}" ng-attr-title="{{link.title}}" ng-click="sidebar.menuCollapse($event)">
        <i ng-if="link.icon" class="{{link.icon}}"></i>
        <span>{{link.name}}</span>
        <i ng-if="link.subitems" class="fa fa-angle-left pull-right"></i>
    </a>
    <ul class="treeview-menu" ng-class="{active:links.activeSubmenu(link)}" ng-if="link.subitems">
        <li ng-repeat="link in link.subitems" ng-class="{active:links.activeLink(link)}" ng-include="'subnav'">
        </li>
    </ul>
</script>`;


export const navbarDefaults = {
    theme: 'default',
    search_text: '',
    // Navigation place on top of the page (add navbar-static-top class to navbar)
    // nabar2 it is always placed on top
    top: false,
    // Fixed navbar
    fixed: false,
    search: false,
    url: '/',
    target: '_self',
    toggle: true,
    fluid: true,
    expanding: noop,
    expanded: noop,
    collapsing: noop,
    collapsed: noop,
    isCollapsed: true
};


export const sidebarDefaults = {
    open: false,
    toggleName: 'Menu',
    infoText: 'Signed in as'
};
