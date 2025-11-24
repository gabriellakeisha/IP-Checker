# use Ruby Alpine for smaller image size
FROM ruby:3.2-alpine

# install dependencies
RUN apk add --no-cache build-base

# set working directory
WORKDIR /app

# copy Gemfile
COPY Gemfile ./

# install gems
RUN bundle install --without development

# copy application code
COPY src/ ./

# expose port 80
EXPOSE 80

# set environment variable for port
ENV PORT=80

# run the application
CMD ["ruby", "app.rb"]