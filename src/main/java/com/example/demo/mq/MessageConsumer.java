package com.example.demo.mq;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.example.demo.config.RabbitMQConfig;
import com.example.demo.model.Question;
import com.example.demo.service.QuestionService;

@Component
public class MessageConsumer {

    @Autowired
    private QuestionService orderService;

    private static final Logger logger = LoggerFactory.getLogger(MessageConsumer.class);

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveQuestion(Question event) {
        logger.info("message {} consumed", event);
        orderService.addques(event);
    }
}
