"""
Pytest fixtures for OmniRun test suite.

These fixtures provide test environments for all test categories.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any, List
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Core Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def omni_runner(temp_dir) -> 'OmniRun':
    """Create an OmniRun instance with temp directory."""
    # Import here to avoid module-level issues
    from omni_run import OmniRun
    return OmniRun(str(temp_dir), verbose=True)


@pytest.fixture
def omni_runner_with_config(temp_dir) -> 'OmniRun':
    """Create an OmniRun instance with custom config."""
    from omni_run import OmniRun
    
    config_file = temp_dir / ".omnirun.yaml"
    config_file.write_text("""
auto_fix: true
max_depth: 5
timeout: 300
exclude_dirs: []
""")
    
    return OmniRun(str(temp_dir), verbose=True, config_file=str(config_file))


# ============================================================================
# Python Project Fixtures
# ============================================================================

@pytest.fixture
def python_simple_script(temp_dir) -> Path:
    """Create a simple Python script."""
    script = temp_dir / "hello.py"
    script.write_text('print("Hello, World!")')
    return script


@pytest.fixture
def python_main_pattern(temp_dir) -> Path:
    """Create a Python file matching main patterns."""
    script = temp_dir / "main.py"
    script.write_text('''
import sys

def main():
    print("Main function called")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''')
    return script


@pytest.fixture
def python_flask_app(temp_dir) -> Path:
    """Create a Flask application."""
    app_file = temp_dir / "app.py"
    app_file.write_text('''
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run()
''')
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text("flask>=2.0.0\n")
    return app_file


@pytest.fixture
def python_django_app(temp_dir) -> Path:
    """Create a Django-like project structure."""
    # Create manage.py
    manage_py = temp_dir / "manage.py"
    manage_py.write_text('''#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''')
    os.chmod(manage_py, 0o755)
    
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text("django>=4.0.0\n")
    
    return manage_py


@pytest.fixture
def python_fastapi_app(temp_dir) -> Path:
    """Create a FastAPI application."""
    app_file = temp_dir / "main.py"
    app_file.write_text('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
    
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text("fastapi>=0.100.0\nuvicorn>=0.22.0\n")
    
    return app_file


@pytest.fixture
def python_with_venv(temp_dir) -> Path:
    """Create a Python project with virtual environment."""
    script = temp_dir / "app.py"
    script.write_text('''
import sys
print(f"Python: {sys.version}")
''')
    
    # Create venv structure
    venv_dir = temp_dir / "venv"
    venv_lib = venv_dir / "lib" / "python3.12" / "site-packages"
    venv_lib.mkdir(parents=True, exist_ok=True)
    
    # Create python executable in venv
    python_exe = venv_dir / "bin" / "python"
    python_exe.parent.mkdir(parents=True, exist_ok=True)
    python_exe.write_text("#!/bin/bash\necho Python")
    os.chmod(python_exe, 0o755)
    
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text("some-package>=1.0.0\n")
    
    return script


# ============================================================================
# JavaScript/TypeScript Project Fixtures
# ============================================================================

@pytest.fixture
def nodejs_simple_script(temp_dir) -> Path:
    """Create a simple Node.js script."""
    script = temp_dir / "server.js"
    script.write_text('''
const http = require("http");
const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain");
  res.end("Hello World\\n");
});
server.listen(3000);
''')
    return script


@pytest.fixture
def nodejs_express_app(temp_dir) -> Path:
    """Create an Express.js application."""
    # Create package.json
    package_json = temp_dir / "package.json"
    package_json.write_text(json.dumps({
        "name": "express-app",
        "version": "1.0.0",
        "scripts": {
            "start": "node app.js",
            "dev": "nodemon app.js",
            "test": "jest"
        },
        "dependencies": {
            "express": "^4.18.0"
        },
        "devDependencies": {
            "nodemon": "^2.0.0"
        }
    }, indent=2))
    
    # Create app.js
    app_file = temp_dir / "app.js"
    app_file.write_text('''
const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Hello World");
});

app.listen(3000);
''')
    
    return app_file


@pytest.fixture
def nodejs_react_app(temp_dir) -> Path:
    """Create a React application."""
    # Create package.json
    package_json = temp_dir / "package.json"
    package_json.write_text(json.dumps({
        "name": "react-app",
        "version": "1.0.0",
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test"
        },
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "devDependencies": {
            "react-scripts": "5.0.0"
        }
    }, indent=2))
    
    # Create src/index.js
    src_dir = temp_dir / "src"
    src_dir.mkdir(exist_ok=True)
    index_file = src_dir / "index.js"
    index_file.write_text('''
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

ReactDOM.render(<App />, document.getElementById("root"));
''')
    
    return package_json


@pytest.fixture
def nodejs_nextjs_app(temp_dir) -> Path:
    """Create a Next.js application."""
    # Create package.json
    package_json = temp_dir / "package.json"
    package_json.write_text(json.dumps({
        "name": "nextjs-app",
        "version": "1.0.0",
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start"
        },
        "dependencies": {
            "next": "^13.0.0",
            "react": "^18.0.0"
        }
    }, indent=2))
    
    # Create pages/index.js
    pages_dir = temp_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    index_file = pages_dir / "index.js"
    index_file.write_text('''
import Head from "next/head";

export default function Home() {
  return (
    <div>
      <Head>
        <title>Next.js App</title>
      </Head>
      <h1>Welcome to Next.js</h1>
    </div>
  );
}
''')
    
    return package_json


@pytest.fixture
def nodejs_with_node_modules(temp_dir) -> Path:
    """Create a Node.js project with node_modules."""
    script = temp_dir / "app.js"
    script.write_text('''
console.log("App with dependencies");
''')
    
    # Create node_modules (empty directory)
    node_modules = temp_dir / "node_modules"
    node_modules.mkdir(exist_ok=True)
    
    # Create package.json
    package_json = temp_dir / "package.json"
    package_json.write_text(json.dumps({
        "name": "app-with-deps",
        "version": "1.0.0",
        "dependencies": {
            "lodash": "^4.17.0"
        }
    }, indent=2))
    
    return script


# ============================================================================
# Go Project Fixtures
# ============================================================================

@pytest.fixture
def go_simple_program(temp_dir) -> Path:
    """Create a simple Go program."""
    main_file = temp_dir / "main.go"
    main_file.write_text('''
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
''')
    
    # Create go.mod
    go_mod = temp_dir / "go.mod"
    go_mod.write_text('''
module example.com/hello

go 1.21
''')
    
    return main_file


@pytest.fixture
def go_gin_app(temp_dir) -> Path:
    """Create a Gin framework application."""
    main_file = temp_dir / "main.go"
    main_file.write_text('''
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "Hello World",
        })
    })
    r.Run()
}
''')
    
    # Create go.mod
    go_mod = temp_dir / "go.mod"
    go_mod.write_text('''
module gin-app

go 1.21

require github.com/gin-gonic/gin v1.9.0
''')
    
    return main_file


@pytest.fixture
def go_echo_app(temp_dir) -> Path:
    """Create an Echo framework application."""
    main_file = temp_dir / "main.go"
    main_file.write_text('''
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

func main() {
    e := echo.New()
    e.GET("/", func(c echo.Context) error {
        return c.String(http.StatusOK, "Hello, World!")
    })
    e.Start(":8080")
}
''')
    
    # Create go.mod
    go_mod = temp_dir / "go.mod"
    go_mod.write_text('''
module echo-app

go 1.21

require github.com/labstack/echo/v4 v4.11.0
''')
    
    return main_file


# ============================================================================
# Rust Project Fixtures
# ============================================================================

@pytest.fixture
def rust_simple_program(temp_dir) -> Path:
    """Create a simple Rust program."""
    main_file = temp_dir / "main.rs"
    main_file.write_text('''
fn main() {
    println!("Hello, World!");
}
''')
    
    # Create Cargo.toml
    cargo_toml = temp_dir / "Cargo.toml"
    cargo_toml.write_text('''
[package]
name = "hello"
version = "0.1.0"
edition = "2021"

[dependencies]
''')
    
    # Create src directory
    src_dir = temp_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    # Create Cargo.toml in src
    src_cargo = src_dir / "Cargo.toml"
    src_cargo.write_text('[package]\nname = "hello"\nversion = "0.1.0"\nedition = "2021"\n')
    
    return main_file


@pytest.fixture
def rust_actix_app(temp_dir) -> Path:
    """Create an Actix web framework application."""
    main_file = temp_dir / "main.rs"
    main_file.write_text('''
use actix_web::{App, HttpServer, web};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(web::resource("/").to(|| async { "Hello World" }))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
''')
    
    # Create Cargo.toml
    cargo_toml = temp_dir / "Cargo.toml"
    cargo_toml.write_text('''
[package]
name = "actix-app"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4.0"
''')
    
    src_dir = temp_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    return main_file


@pytest.fixture
def rust_rocket_app(temp_dir) -> Path:
    """Create a Rocket web framework application."""
    main_file = temp_dir / "main.rs"
    main_file.write_text('''
#[get("/")]
fn index() -> &'static str {
    "Hello, World!"
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/", routes![index])
}
''')
    
    # Create Cargo.toml
    cargo_toml = temp_dir / "Cargo.toml"
    cargo_toml.write_text('''
[package]
name = "rocket-app"
version = "0.1.0"
edition = "2021"

[dependencies]
rocket = "0.5"
''')
    
    src_dir = temp_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    return main_file


@pytest.fixture
def rust_with_target(temp_dir) -> Path:
    """Create a Rust project that has been built."""
    main_file = temp_dir / "main.rs"
    main_file.write_text('''
fn main() {
    println!("Built Rust app");
}
''')
    
    # Create Cargo.toml
    cargo_toml = temp_dir / "Cargo.toml"
    cargo_toml.write_text('''
[package]
name = "built-app"
version = "0.1.0"
edition = "2021"
''')
    
    # Create target directory
    target_dir = temp_dir / "target"
    target_dir.mkdir(exist_ok=True)
    debug_dir = target_dir / "debug"
    debug_dir.mkdir(exist_ok=True)
    binary = debug_dir / "built-app"
    binary.write_text("#!/bin/bash\necho binary")
    os.chmod(binary, 0o755)
    
    return main_file


# ============================================================================
# Java Project Fixtures
# ============================================================================

@pytest.fixture
def java_maven_app(temp_dir) -> Path:
    """Create a Maven Java application."""
    # Create pom.xml
    pom_xml = temp_dir / "pom.xml"
    pom_xml.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>maven-app</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
            </plugin>
        </plugins>
    </build>
</project>
''')
    
    # Create source directory
    src_dir = temp_dir / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # Create App.java
    app_java = src_dir / "App.java"
    app_java.write_text('''
package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
''')
    
    return pom_xml


@pytest.fixture
def java_spring_boot_app(temp_dir) -> Path:
    """Create a Spring Boot application."""
    # Create pom.xml
    pom_xml = temp_dir / "pom.xml"
    pom_xml.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>spring-boot-app</artifactId>
    <version>1.0.0</version>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.0.0</version>
    </parent>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
''')
    
    # Create source directory
    src_dir = temp_dir / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Application.java
    app_java = src_dir / "Application.java"
    app_java.write_text('''
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
''')
    
    return pom_xml


@pytest.fixture
def java_gradle_app(temp_dir) -> Path:
    """Create a Gradle Java application."""
    # Create build.gradle
    build_gradle = temp_dir / "build.gradle"
    build_gradle.write_text('''
plugins {
    id 'java'
}

group 'com.example'
version '1.0.0'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'com.google.guava:guava:31.1-jre'
    testImplementation 'junit:junit:4.13.2'
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
}
''')
    
    # Create settings.gradle
    settings_gradle = temp_dir / "settings.gradle"
    settings_gradle.write_text("rootProject.name = 'gradle-app'\n")
    
    # Create source directory
    src_dir = temp_dir / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # Create App.java
    app_java = src_dir / "App.java"
    app_java.write_text('''
package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("Hello from Gradle!");
    }
}
''')
    
    return build_gradle


# ============================================================================
# Ruby Project Fixtures
# ============================================================================

@pytest.fixture
def ruby_simple_script(temp_dir) -> Path:
    """Create a simple Ruby script."""
    script = temp_dir / "hello.rb"
    script.write_text('#!/usr/bin/env ruby\nputs "Hello, World!"\n')
    return script


@pytest.fixture
def ruby_rails_app(temp_dir) -> Path:
    """Create a Ruby on Rails application."""
    # Create Gemfile
    gemfile = temp_dir / "Gemfile"
    gemfile.write_text('''
source "https://rubygems.org"

ruby "3.0.0"

gem "rails", "~> 7.0.0"
gem "sqlite3", "~> 1.4"
''')
    
    # Create Gemfile.lock
    gemfile_lock = temp_dir / "Gemfile.lock"
    gemfile_lock.write_text('''
GEM
  remote: https://rubygems.org/
  specs:
    rails (7.0.0)
      actioncable (= 7.0.0)
      actionmailbox (= 7.0.0)
      actionpack (= 7.0.0)
      actiontext (= 7.0.0)
      actionview (= 7.0.0)
      activejob (= 7.0.0)
      activemodel (= 7.0.0)
      activerecord (= 7.0.0)
      activestorage (= 7.0.0)
      activesupport (= 7.0.0)
      bundler (>= 1.15.0)
      railties (= 7.0.0)
PLATFORMS
  ruby
DEPENDENCIES
  rails (~> 7.0.0)
  sqlite3 (~> 1.4)
RUBY VERSION
   ruby 3.0.0p0
''')
    
    # Create config.ru
    config_ru = temp_dir / "config.ru"
    config_ru.write_text('''
# This file is used by Rack-based servers to start the application.

require_relative "config/environment"

run Rails.application
''')
    
    return gemfile


# ============================================================================
# PHP Project Fixtures
# ============================================================================

@pytest.fixture
def php_simple_script(temp_dir) -> Path:
    """Create a simple PHP script."""
    script = temp_dir / "hello.php"
    script.write_text('<?php\necho "Hello, World!";\n')
    return script


@pytest.fixture
def php_laravel_app(temp_dir) -> Path:
    """Create a Laravel application."""
    # Create composer.json
    composer_json = temp_dir / "composer.json"
    composer_json.write_text(json.dumps({
        "name": "laravel/laravel",
        "type": "project",
        "description": "The Laravel Framework.",
        "keywords": ["framework", "laravel"],
        "require": {
            "php": "^8.1",
            "laravel/framework": "^10.0"
        },
        "require-dev": {
            "fakerphp/faker": "^1.9.1"
        }
    }, indent=2))
    
    # Create artisan
    artisan = temp_dir / "artisan"
    artisan.write_text('#!/usr/bin/env php\n<?php\ndefine(\'LARAVEL_START\', microtime(true));\n// Laravel bootstrap...\n')
    os.chmod(artisan, 0o755)
    
    return composer_json


# ============================================================================
# C/C++ Project Fixtures
# ============================================================================

@pytest.fixture
def cpp_simple_program(temp_dir) -> Path:
    """Create a simple C++ program."""
    main_file = temp_dir / "main.cpp"
    main_file.write_text('''
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
''')
    return main_file


@pytest.fixture
def c_simple_program(temp_dir) -> Path:
    """Create a simple C program."""
    main_file = temp_dir / "main.c"
    main_file.write_text('''
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
''')
    return main_file


# ============================================================================
# Task Runner Fixtures
# ============================================================================

@pytest.fixture
def makefile_project(temp_dir) -> Path:
    """Create a project with Makefile."""
    # Create Makefile
    makefile = temp_dir / "Makefile"
    makefile.write_text('''
.PHONY: all clean test run

all: run

test:
	@echo "Running tests..."

run: app.py
	python app.py

clean:
	rm -f *.pyc __pycache__
''')
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from Makefile project")\n')
    
    return makefile


@pytest.fixture
def justfile_project(temp_dir) -> Path:
    """Create a project with justfile."""
    # Create justfile
    justfile = temp_dir / "justfile"
    justfile.write_text('''
default:
    @echo "Running default task"

test:
    @echo "Running tests..."

run:
    @python app.py

deploy:
    @echo "Deploying..."
''')
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from justfile project")\n')
    
    return justfile


@pytest.fixture
def taskfile_project(temp_dir) -> Path:
    """Create a project with Taskfile.yml."""
    import yaml
    
    # Create Taskfile.yml
    taskfile = temp_dir / "Taskfile.yml"
    taskfile.write_text('''
version: "3"

tasks:
  default:
    cmds:
      - python app.py

  test:
    cmds:
      - echo "Running tests..."

  build:
    cmds:
      - echo "Building..."
''')
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from Taskfile project")\n')
    
    return taskfile


# ============================================================================
# Container Fixtures
# ============================================================================

@pytest.fixture
def dockerfile_project(temp_dir) -> Path:
    """Create a project with Dockerfile."""
    # Create Dockerfile
    dockerfile = temp_dir / "Dockerfile"
    dockerfile.write_text('''
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
''')
    
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text("flask>=2.0.0\n")
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from Docker")\n')
    
    return dockerfile


@pytest.fixture
def docker_compose_project(temp_dir) -> Path:
    """Create a project with docker-compose.yml."""
    import yaml
    
    # Create docker-compose.yml
    compose_file = temp_dir / "docker-compose.yml"
    compose_file.write_text('''
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    working_dir: /app
''')
    
    # Create Dockerfile
    dockerfile = temp_dir / "Dockerfile"
    dockerfile.write_text('''
FROM python:3.12-slim
WORKDIR /app
RUN pip install flask
COPY . .
CMD ["python", "app.py"]
''')
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from Docker Compose")\n')
    
    return compose_file


@pytest.fixture
def conda_environment(temp_dir) -> Path:
    """Create a conda environment file."""
    # Create environment.yml
    env_file = temp_dir / "environment.yml"
    env_file.write_text('''
name: myproject
channels:
  - defaults
  - conda-forge
dependencies:
  - python>=3.10
  - numpy
  - pandas
  - matplotlib
  - pip
  - pip:
    - torch
''')
    
    # Create app.py
    app_file = temp_dir / "app.py"
    app_file.write_text('print("Hello from Conda")\n')
    
    return env_file


# ============================================================================
# Multi-language Project Fixtures
# ============================================================================

@pytest.fixture
def multi_language_project(temp_dir) -> Path:
    """Create a project with multiple languages."""
    # Create Python file
    (temp_dir / "api.py").write_text('''
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "API Running"
''')
    
    # Create requirements.txt
    (temp_dir / "requirements.txt").write_text("flask>=2.0.0\n")
    
    # Create JavaScript file
    frontend_dir = temp_dir / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "index.js").write_text('console.log("Frontend");\n')
    
    # Create package.json
    (frontend_dir / "package.json").write_text(json.dumps({
        "name": "frontend",
        "scripts": {"build": "echo build"}
    }))
    
    # Create Go file
    (temp_dir / "main.go").write_text('''
package main
import "fmt"
func main() { fmt.Println("Go service") }
''')
    
    # Create go.mod
    (temp_dir / "go.mod").write_text("module multilang\ngo 1.21\n")
    
    return temp_dir


# ============================================================================
# Edge Case Fixtures
# ============================================================================

@pytest.fixture
def empty_directory(temp_dir) -> Path:
    """Create an empty directory."""
    return temp_dir


@pytest.fixture
def hidden_directory(temp_dir) -> Path:
    """Create a directory with hidden files."""
    hidden = temp_dir / ".hidden"
    hidden.mkdir()
    (hidden / "secret.py").write_text('print("hidden")\n')
    return temp_dir


@pytest.fixture
def deep_directory_structure(temp_dir) -> Path:
    """Create a deep directory structure."""
    current = temp_dir
    for i in range(10):
        current = current / f"level_{i}"
        current.mkdir()
        (current / f"file_{i}.py").write_text(f'# Level {i}\nprint("level {i}")\n')
    return temp_dir


@pytest.fixture
def mixed_extensions(temp_dir) -> Path:
    """Create files with mixed extensions."""
    (temp_dir / "file.py").write_text("print('py')\n")
    (temp_dir / "file.js").write_text("console.log('js')\n")
    (temp_dir / "file.ts").write_text("console.log('ts')\n")
    (temp_dir / "file.go").write_text("package main\n")
    (temp_dir / "file.rs").write_text("fn main() {}\n")
    (temp_dir / "file.txt").write_text("text file\n")
    return temp_dir


@pytest.fixture
def binary_file(temp_dir) -> Path:
    """Create a binary executable file."""
    binary = temp_dir / "app"
    binary.write_bytes(b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    os.chmod(binary, 0o755)
    return binary


@pytest.fixture
def file_with_shebang(temp_dir) -> Path:
    """Create a file with shebang."""
    script = temp_dir / "script.sh"
    script.write_text('#!/bin/bash\necho "Shebang script"\n')
    os.chmod(script, 0o755)
    return script


@pytest.fixture
def invalid_python_file(temp_dir) -> Path:
    """Create an invalid Python file."""
    script = temp_dir / "broken.py"
    script.write_text('''
def broken_function():
    this_will_cause_a_syntax_error
    because_we_forgot_the_colon
''')
    return script


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def custom_config_file(temp_dir) -> Path:
    """Create a custom configuration file."""
    config_file = temp_dir / ".omnirun.yaml"
    config_file.write_text('''
auto_fix: true
enable_backup: true
auto_rollback: true
confirm_each_command: false
max_depth: 5
exclude_dirs:
  - node_modules
  - .git
timeout: 600
preferred_commands:
  "Python:main.py": "python main.py --production"
''')
    return config_file


@pytest.fixture
def json_config_file(temp_dir) -> Path:
    """Create a JSON configuration file."""
    config_file = temp_dir / "omnirun.json"
    config_file.write_text(json.dumps({
        "auto_fix": True,
        "max_depth": 10,
        "timeout": 300,
        "exclude_dirs": ["node_modules", "__pycache__"]
    }, indent=2))
    return config_file


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def mock_interpreter_check(monkeypatch):
    """Mock interpreter availability checks."""
    def mock_check(interpreter):
        if interpreter in ['python3', 'python']:
            return True, '3.12.0'
        elif interpreter == 'node':
            return True, '20.0.0'
        elif interpreter == 'go':
            return True, '1.21.0'
        elif interpreter == 'cargo':
            return True, '1.73.0'
        else:
            return False, None
    
    monkeypatch.setattr('omni_run.OmniRun.check_interpreter_available', mock_check)


@pytest.fixture
def disable_venv_detection(monkeypatch):
    """Disable virtual environment detection."""
    def mock_detect(*args, **kwargs):
        return None
    
    monkeypatch.setattr('omni_run.OmniRun.detect_environment', mock_detect)

